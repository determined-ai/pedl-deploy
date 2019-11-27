import sys

import boto3


ec2 = boto3.client('ec2')


def get_ec2_info(instance_id):
    response = ec2.describe_instances(
        InstanceIds=[
            instance_id
        ]
    )
    return response['Reservations'][0]['Instances'][0]


def get_latest_release_amis():
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


def check_keypair(name):
    all_keys = ec2.describe_key_pairs()['KeyPairs']
    names = [x['KeyName'] for x in all_keys]

    if name in names:
        return True

    print(f'Key pair {name} not found. Please create key pair first')
    sys.exit(1)
