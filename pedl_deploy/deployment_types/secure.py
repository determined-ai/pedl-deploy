import pkg_resources

from pedl_deploy.cfn import deploy_stack, get_output
from pedl_deploy.constants import *
from pedl_deploy.deployment_types.base import PEDLDeployment
from pedl_deploy.ec2 import get_ec2_info


class Secure(PEDLDeployment):
    ssh_command = 'SSH to PEDL Master: ssh -i  <keypair> ubuntu@{master_ip} -o ' \
                  '"proxycommand ssh -W %h:%p -i <keypair> ubuntu@{bastion_ip}"'
    pedl_ui = 'To View PEDL UI:\n' \
              'Add Keypair: ssh-add <keypair>\n' \
              'Open SSH Tunnel through Bastion:  ssh -N -L 8080:{master_ip}:8080 ubuntu@{bastion_ip}\n' \
              'View the PEDL UI: http://localhost:8080'


    def __init__(self, parameters):
        template = pkg_resources.resource_filename('pedl_deploy.templates', 'secure.yaml')
        super().__init__(template, parameters)

    def deploy(self):
        parameters = self.parameters()
        cfn_parameters = [
            {
                'ParameterKey': cloudformation.USER_NAME_KEY,
                'ParameterValue': parameters[pedl_config.USER]
            },
            {
                'ParameterKey': cloudformation.KEYPAIR_KEY,
                'ParameterValue': parameters[pedl_config.KEYPAIR]
            },
            {
                'ParameterKey': cloudformation.BASTION_AMI_KEY,
                'ParameterValue': defaults.BASTION_AMI
            },
            {
                'ParameterKey': cloudformation.MASTER_AMI_KEY,
                'ParameterValue': parameters[pedl_config.MASTER_AMI]
            },
            {
                'ParameterKey': cloudformation.MASTER_INSTANCE_TYPE,
                'ParameterValue': parameters[pedl_config.MASTER_INSTANCE_TYPE]
            },
            {
                'ParameterKey': cloudformation.AGENT_AMI_KEY,
                'ParameterValue': parameters[pedl_config.AGENT_AMI]
            },
            {
                'ParameterKey': cloudformation.AGENT_INSTANCE_TYPE,
                'ParameterValue': parameters[pedl_config.AGENT_INSTANCE_TYPE]
            }
        ]

        with open(self.template()) as f:
            template = f.read()

        deploy_stack(parameters[pedl_config.PEDL_STACK_NAME], template, parameters=cfn_parameters)
        self.print_results(parameters[pedl_config.PEDL_STACK_NAME])

    def print_results(self, stack_name):
        output = get_output(stack_name)

        bastion_ip = get_ec2_info(output['BastionId'])[cloudformation.PUBLIC_IP_ADDRESS]
        master_ip = get_ec2_info(output['MasterId'])[cloudformation.PRIVATE_IP_ADDRESS]

        ui_command = self.pedl_ui.format(master_ip=master_ip, bastion_ip=bastion_ip)
        print(ui_command)
        print()

        ssh_command = self.ssh_command.format(master_ip=master_ip, bastion_ip=bastion_ip)
        print(ssh_command)
        print()
