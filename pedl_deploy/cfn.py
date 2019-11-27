import sys

import boto3
from botocore.exceptions import ClientError, WaiterError

cfn = boto3.client('cloudformation')
delete_waiter = cfn.get_waiter('stack_delete_complete')
create_waiter = cfn.get_waiter('stack_create_complete')
update_waiter = cfn.get_waiter('stack_update_complete')


def validate_stack(template_body):
    cfn.validate_template(TemplateBody=template_body)


def stack_exists(stack_name):
    try:
        cfn.describe_stacks(StackName=stack_name)
    except ClientError:
        print(f'{stack_name} not found')
        return False
    return True


def delete_stack(stack_name):
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


def update_stack(stack_name, template_body, parameters=None):
    print(f'Updating stack {stack_name}')

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


def create_stack(stack_name, template_body, parameters=None):
    print(f'Creating stack {stack_name}')
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


def get_output(stack_name):
    response = cfn.describe_stacks(StackName=stack_name)
    response_dict = {}

    for output in response['Stacks'][0]['Outputs']:
        k, v = output['OutputKey'], output['OutputValue']
        response_dict[k] = v
    return response_dict


def deploy_stack(stack_name, template_body, parameters=None):
    validate_stack(template_body)

    if stack_exists(stack_name):
        update_stack(stack_name, template_body, parameters)
    else:
        create_stack(stack_name, template_body, parameters)
