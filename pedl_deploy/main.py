import argparse

import boto3

from pedl_deploy.cfn import get_output, delete_stack
from pedl_deploy.constants import *
from pedl_deploy.ec2 import get_latest_release_amis
from pedl_deploy.s3 import empty_bucket
from pedl_deploy.deployment_types.simple import Simple
from pedl_deploy.deployment_types.secure import Secure
from pedl_deploy.deployment_types.vpc import VPC

sts = boto3.client('sts')


def get_user():
    response = sts.get_caller_identity()
    return response['Arn'].split('/')[-1]


def delete(stack_name):
    bucket_name = get_output(stack_name).get(cloudformation.CHECKPOINT_BUCKET)
    if bucket_name:
        empty_bucket(bucket_name)

    delete_stack(stack_name)


def main():
    master_ami, agent_ami = get_latest_release_amis()

    parser = argparse.ArgumentParser(description='Package for deploying PEDL to AWS')
    parser.add_argument('--delete', action='store_true',
                        help='Delete PEDL from account')
    parser.add_argument('--deployment-type', type=str, default=defaults.DEPLOYMENT_TYPE,
                        help=f'deployment type - must be one of [{", ".join(deployment_types.DEPLOYMENT_TYPES)}]')
    parser.add_argument('--master-ami', type=str, default=master_ami,
                        help='ami for pedl master')
    parser.add_argument('--agent-ami', type=str, default=agent_ami,
                        help='ami for pedl agent')
    parser.add_argument('--keypair', type=str, default=defaults.KEYPAIR_NAME,
                        help='keypair for master and agent')
    parser.add_argument('--master-instance-type', type=str,
                        default=defaults.MASTER_INSTANCE_TYPE,
                        help='instance type for master')
    parser.add_argument('--agent-instance-type', type=str,
                        default=defaults.AGENT_INSTANCE_TYPE,
                        help='instance type for agent')
    args = parser.parse_args()

    user = get_user()
    stack_name = defaults.PEDL_STACK_NAME_BASE.format(user)

    if args.delete:
        delete(stack_name)
        print('Delete Successful')
        return

    pedl_configs = {
        pedl_config.MASTER_AMI: args.master_ami,
        pedl_config.AGENT_AMI: args.agent_ami,
        pedl_config.KEYPAIR: args.keypair,
        pedl_config.MASTER_INSTANCE_TYPE: args.master_instance_type,
        pedl_config.AGENT_INSTANCE_TYPE: args.agent_instance_type,
        pedl_config.USER: user,
        pedl_config.PEDL_STACK_NAME: stack_name
    }

    deployment_type_map = {
        deployment_types.SIMPLE: Simple,
        deployment_types.SECURE: Secure,
        deployment_types.VPC: VPC
    }

    assert args.deployment_type in deployment_types.DEPLOYMENT_TYPES, \
        f'deployment type - must be one of [{", ".join(deployment_types.DEPLOYMENT_TYPES)}]'

    deployment_object = deployment_type_map[args.deployment_type](pedl_configs)

    print('Starting PEDL Deployment')
    deployment_object.deploy()
    print('PEDL Deployment Successful')


if __name__ == '__main__':
    main()
