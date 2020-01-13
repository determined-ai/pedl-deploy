import argparse
import sys

from pedl_deploy.aws import get_output, delete_stack, session, empty_bucket, get_latest_release_amis, check_keypair
from pedl_deploy.constants import *
from pedl_deploy.deployment_types.simple import Simple
from pedl_deploy.deployment_types.secure import Secure
from pedl_deploy.deployment_types.vpc import VPC


def get_user(boto3_session):
    sts = boto3_session.client('sts')
    response = sts.get_caller_identity()
    return response['Arn'].split('/')[-1]


def delete(stack_name, boto3_session):
    bucket_name = get_output(stack_name, boto3_session).get(cloudformation.CHECKPOINT_BUCKET)
    if bucket_name:
        empty_bucket(bucket_name, boto3_session)

    delete_stack(stack_name, boto3_session)


def main():
    parser = argparse.ArgumentParser(description='Package for deploying PEDL to AWS')
    parser.add_argument('--delete', action='store_true',
                        help='Delete PEDL from account')
    parser.add_argument('--deployment-type', type=str, default=defaults.DEPLOYMENT_TYPE,
                        help=f'deployment type - must be one of [{", ".join(deployment_types.DEPLOYMENT_TYPES)}]')
    parser.add_argument('--master-ami', type=str, default=None,
                        help='ami for pedl master')
    parser.add_argument('--agent-ami', type=str, default=None,
                        help='ami for pedl agent')
    parser.add_argument('--keypair', type=str, default=defaults.KEYPAIR_NAME,
                        help='keypair for master and agent')
    parser.add_argument('--master-instance-type', type=str,
                        default=defaults.MASTER_INSTANCE_TYPE,
                        help='instance type for master')
    parser.add_argument('--agent-instance-type', type=str,
                        default=defaults.AGENT_INSTANCE_TYPE,
                        help='instance type for agent')
    parser.add_argument('--user', type=str,
                        default=None,
                        help='user to name stack and tag resources')
    parser.add_argument('--aws-profile', type=str,
                        default=None,
                        help='aws profile for deploying')
    args = parser.parse_args()

    boto3_session = session(args.aws_profile)

    check_keypair(args.keypair, boto3_session)

    if args.master_ami and args.agent_ami:
        master_ami, agent_ami = args.master_ami, args.agent_ami
    else:
        if args.aws_profile:
            print('Profile must explicitly set ami ids')
            sys.exit(1)

        master_ami, agent_ami = get_latest_release_amis(boto3_session)

    if args.user:
        user = args.user
    else:
        user = get_user(boto3_session)

    stack_name = defaults.PEDL_STACK_NAME_BASE.format(user)
    if args.delete:
        delete(stack_name, boto3_session)
        print('Delete Successful')
        return

    pedl_configs = {
        pedl_config.MASTER_AMI: master_ami,
        pedl_config.AGENT_AMI: agent_ami,
        pedl_config.KEYPAIR: args.keypair,
        pedl_config.MASTER_INSTANCE_TYPE: args.master_instance_type,
        pedl_config.AGENT_INSTANCE_TYPE: args.agent_instance_type,
        pedl_config.USER: user,
        pedl_config.PEDL_STACK_NAME: stack_name,
        pedl_config.BOTO3_SESSION: boto3_session
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
