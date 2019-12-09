import argparse
import pkg_resources
import sys
import yaml

from pedl_deploy.cfn import deploy_stack, get_output, delete_stack
from pedl_deploy.constants import *
from pedl_deploy.ec2 import get_latest_release_amis, get_ec2_info
from pedl_deploy.s3 import empty_bucket


def display_secure_config(resources_output, pedl_configs):
    master = master_config.DEFAULT_MASTER_CONFIGS.copy()
    provisioner = master[master_config.PROVISIONER]

    provisioner[master_config.IAM_INSTANCE_PROFILE_ARN] = resources_output[cloudformation.AGENT_INSTANCE_PROFILE_KEY]
    provisioner[master_config.INSTANCE_TYPE] = pedl_configs[pedl_config.AGENT_INSTANCE_TYPE]
    provisioner[master_config.SSH_KEY_NAME] = pedl_configs[pedl_config.KEYPAIR]
    provisioner[master_config.IMAGE_ID] = pedl_configs[pedl_config.AGENT_AMI]

    provisioner[master_config.NETWORK_INTERFACE][master_config.SUBNET_ID] = resources_output[cloudformation.PRIVATE_SUBNET_KEY]
    provisioner[master_config.NETWORK_INTERFACE][master_config.SECURITY_GROUP_ID] = resources_output[cloudformation.AGENT_SECURITY_GROUP_ID_KEY]

    print(f'Insert configs to {misc.PEDL_MASTER_YAML_PATH} on master instance')
    print(yaml.dump(master_config.DEFAULT_MASTER_CONFIGS))

    print()
    master_ip = get_ec2_info(resources_output[cloudformation.MASTER_ID])['PrivateIpAddress']
    bastion_ip = get_ec2_info(resources_output[cloudformation.BASTION_ID])['PublicIpAddress']
    ssh_command = misc.SECURE_SSH_COMMAND.format(master_ip=master_ip, bastion_ip=bastion_ip)
    print(f'ssh to master using: {ssh_command}')


def display_simple_config(resources_output, pedl_configs):
    master = master_config.DEFAULT_MASTER_CONFIGS.copy()
    provisioner = master[master_config.PROVISIONER]

    provisioner[master_config.IAM_INSTANCE_PROFILE_ARN] = resources_output[cloudformation.AGENT_INSTANCE_PROFILE_KEY]
    provisioner[master_config.INSTANCE_TYPE] = pedl_configs[pedl_config.AGENT_INSTANCE_TYPE]
    provisioner[master_config.SSH_KEY_NAME] = pedl_configs[pedl_config.KEYPAIR]
    provisioner[master_config.IMAGE_ID] = pedl_configs[pedl_config.AGENT_AMI]
    provisioner[master_config.NETWORK_INTERFACE][master_config.SECURITY_GROUP_ID] = resources_output[cloudformation.AGENT_SECURITY_GROUP_ID_KEY]
    provisioner[master_config.NETWORK_INTERFACE][master_config.PUBLIC_IP] = True

    print(f'Insert configs to {misc.PEDL_MASTER_YAML_PATH} on master instance')
    print(yaml.dump(master_config.DEFAULT_MASTER_CONFIGS))

    print()
    master_ip = get_ec2_info(resources_output[cloudformation.MASTER_ID])['PublicIpAddress']
    ssh_command = misc.SIMPLE_SSH_COMMAND.format(master_ip=master_ip)

    print(f'ssh to master using: {ssh_command}')


def deploy_full(pedl_configs):
    print('Starting PEDL deployment')

    cfn_parameters = [
        {
            'ParameterKey': cloudformation.ENVIRONMENT_NAME_KEY,
            'ParameterValue': defaults.ENVIRONMENT_NAME
        },
        {
            'ParameterKey': cloudformation.KEYPAIR_KEY,
            'ParameterValue': pedl_configs[pedl_config.KEYPAIR]
        },
        {
            'ParameterKey': cloudformation.BASTION_AMI_KEY,
            'ParameterValue': defaults.BASTION_AMI
        },
        {
            'ParameterKey': cloudformation.MASTER_AMI_KEY,
            'ParameterValue': pedl_configs[pedl_config.MASTER_AMI]
        },
        {
            'ParameterKey': cloudformation.MASTER_INSTANCE_TYPE,
            'ParameterValue': pedl_configs[pedl_config.MASTER_INSTANCE_TYPE]
        }
    ]

    template_path = pkg_resources.resource_filename('pedl_deploy.templates', resources.SECURE)
    with open(template_path) as f:
        template = f.read()

    deploy_stack(stacks.PEDL_STACK_NAME, template, parameters=cfn_parameters)
    resources_output = get_output(stacks.PEDL_STACK_NAME)
    print(resources_output)
    display_secure_config(resources_output, pedl_configs)


def deploy_simple(pedl_configs):
    print('Starting PEDL deployment')

    resources_cfn_parameters = [
        {
            'ParameterKey': cloudformation.ENVIRONMENT_NAME_KEY,
            'ParameterValue': defaults.ENVIRONMENT_NAME
        },
        {
            'ParameterKey': cloudformation.KEYPAIR_KEY,
            'ParameterValue': pedl_configs[pedl_config.KEYPAIR]
        },
        {
            'ParameterKey': cloudformation.MASTER_AMI_KEY,
            'ParameterValue': pedl_configs[pedl_config.MASTER_AMI]
        },
        {
            'ParameterKey': cloudformation.MASTER_INSTANCE_TYPE,
            'ParameterValue': pedl_configs[pedl_config.MASTER_INSTANCE_TYPE]
        }
    ]

    template_path = pkg_resources.resource_filename('pedl_deploy.templates', resources.SIMPLE)
    with open(template_path) as f:
        template = f.read()

    deploy_stack(stacks.PEDL_STACK_NAME, template, parameters=resources_cfn_parameters)
    resources_output = get_output(stacks.PEDL_STACK_NAME)
    print(resources_output)

    display_simple_config(resources_output, pedl_configs)


def delete():
    bucket_name = get_output(stacks.PEDL_STACK_NAME).get(cloudformation.CHECKPOINT_BUCKET)
    if bucket_name:
        empty_bucket(bucket_name)

    delete_stack(stacks.PEDL_STACK_NAME)


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

    pedl_configs = {
        pedl_config.MASTER_AMI: args.master_ami,
        pedl_config.AGENT_AMI: args.agent_ami,
        pedl_config.KEYPAIR: args.keypair,
        pedl_config.MASTER_INSTANCE_TYPE: args.master_instance_type,
        pedl_config.AGENT_INSTANCE_TYPE: args.agent_instance_type,
    }

    if args.delete:
        delete()
    else:
        if args.deployment_type == deployment_types.SECURE:
            deploy_full(pedl_configs)
        elif args.deployment_type == deployment_types.SIMPLE:
            deploy_simple(pedl_configs)
        else:
            print(f'deployment type - must be one of [{", ".join(deployment_types.DEPLOYMENT_TYPES)}]')
            sys.exit(1)


if __name__ == '__main__':
    main()
