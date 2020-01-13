import sys

import boto3
from botocore.exceptions import ClientError, WaiterError


def session(profile_name):
    return boto3.Session(profile_name=profile_name)


# Cloudformation
def stack_exists(stack_name, boto3_session):
    cfn = boto3_session.client('cloudformation')

    try:
        cfn.describe_stacks(StackName=stack_name)
    except ClientError:
        print(f'{stack_name} not found')
        return False
    return True


def delete_stack(stack_name, boto3_session):
    cfn = boto3_session.client('cloudformation')
    delete_waiter = cfn.get_waiter('stack_delete_complete')

    print(f'Deleting stack {stack_name}')
    cfn.delete_stack(StackName=stack_name)
    try:
        delete_waiter.wait(StackName=stack_name,
                           WaiterConfig={
                               'Delay': 10
                           })
    except WaiterError as e:
        print(e)
        sys.exit(1)


def update_stack(stack_name, template_body, boto3_session, parameters=None):
    print(f'Updating stack {stack_name}')
    cfn = boto3_session.client('cloudformation')
    update_waiter = cfn.get_waiter('stack_update_complete')

    try:
        if parameters:
            cfn.update_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=parameters,
                Capabilities=[
                    'CAPABILITY_IAM',
                ],
            )
        else:
            cfn.update_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Capabilities=[
                    'CAPABILITY_IAM',
                ]
            )
    except ClientError as e:
        if not str(e).endswith('No updates are to be performed.'):
            print(e)
            sys.exit(1)
        else:
            print(f'No Updates to {stack_name}')
            return

    try:
        update_waiter.wait(StackName=stack_name,
                           WaiterConfig={
                               'Delay': 10
                           })

    except WaiterError as e:
        print(e)
        sys.exit(1)


def create_stack(stack_name, template_body, boto3_session, parameters=None):
    print(f'Creating stack {stack_name}')
    cfn = boto3_session.client('cloudformation')
    create_waiter = cfn.get_waiter('stack_create_complete')

    if parameters:
        cfn.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=parameters,
            Capabilities=[
                'CAPABILITY_IAM',
            ],
        )
    else:
        cfn.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Capabilities=[
                'CAPABILITY_IAM',
            ]
        )
    try:
        create_waiter.wait(StackName=stack_name,
                           WaiterConfig={
                               'Delay': 10
                           })

    except WaiterError as e:
        print(e)
        sys.exit(1)


def get_output(stack_name, boto3_session):
    cfn = boto3_session.client('cloudformation')
    response = cfn.describe_stacks(StackName=stack_name)
    response_dict = {}

    for output in response['Stacks'][0]['Outputs']:
        k, v = output['OutputKey'], output['OutputValue']
        response_dict[k] = v
    return response_dict


def deploy_stack(stack_name, template_body, boto3_session, parameters=None):
    cfn = boto3_session.client('cloudformation')
    cfn.validate_template(TemplateBody=template_body)

    if stack_exists(stack_name, boto3_session):
        update_stack(stack_name, template_body, boto3_session, parameters)
    else:
        create_stack(stack_name, template_body, boto3_session, parameters)


# EC2
def get_ec2_info(instance_id, boto3_session):
    ec2 = boto3_session.client('ec2')

    response = ec2.describe_instances(
        InstanceIds=[
            instance_id
        ]
    )
    return response['Reservations'][0]['Instances'][0]


def get_latest_release_amis(boto3_session):
    ec2 = boto3_session.client('ec2')

    response = ec2.describe_images(
        Filters=[
            {
                'Name': 'tag:image_type',
                'Values': [
                    'release',
                ]
            },
        ],

        Owners=['self']
    )

    images = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)
    agent_image, master_image = None, None
    agent_version, master_version = None, None
    for image in images:
        if 'agent' in image['Name']:
            agent_image = image['ImageId']
            for tag in image['Tags']:
                if tag['Key'] == 'pedl-version':
                    agent_version = tag['Value']
            break

    for image in images:
        if 'master' in image['Name']:
            master_image = image['ImageId']
            for tag in image['Tags']:
                if tag['Key'] == 'pedl-version':
                    master_version = tag['Value']
            break

    assert master_version == agent_version
    return master_image, agent_image


def check_keypair(name, boto3_session):
    ec2 = boto3_session.client('ec2')

    all_keys = ec2.describe_key_pairs()['KeyPairs']
    names = [x['KeyName'] for x in all_keys]

    if name in names:
        return True

    print(f'Key pair {name} not found. Please create key pair first')
    sys.exit(1)


# S3
def empty_bucket(bucket_name, boto3_session):
    s3 = boto3_session.resource('s3')
    bucket = s3.Bucket(bucket_name)
    bucket.objects.all().delete()