class deployment_types:
    SIMPLE = 'simple'
    SECURE = 'secure'
    VPC = 'vpc'
    DEPLOYMENT_TYPES = [SIMPLE, SECURE, VPC]

class defaults:
    KEYPAIR_NAME = "pedl-keypair"
    MASTER_INSTANCE_TYPE = 't2.medium'
    AGENT_INSTANCE_TYPE = 'p2.8xlarge'
    BASTION_AMI = 'ami-06d51e91cea0dac8d'
    DEPLOYMENT_TYPE = deployment_types.SIMPLE
    PEDL_STACK_NAME_BASE = "pedl-{}"

class pedl_config:
    MASTER_AMI = 'master_ami'
    AGENT_AMI = 'agent_ami'
    KEYPAIR = 'keypair'
    MASTER_INSTANCE_TYPE = 'master_instance_type'
    AGENT_INSTANCE_TYPE = 'agent_instance_type'
    PEDL_STACK_NAME = 'stack_name'
    USER = 'user'


class cloudformation:
    USER_NAME_KEY = 'UserName'
    KEYPAIR_KEY = 'Keypair'
    VPC_KEY = 'VPC'
    PUBLIC_SUBNET_KEY = 'PublicSubnetId'
    PRIVATE_SUBNET_KEY = 'PrivateSubnetId'
    BASTION_AMI_KEY = 'BastionAmiId'
    MASTER_AMI_KEY = 'MasterAmiId'
    AGENT_AMI_KEY = 'AgentAmiId'
    AGENT_INSTANCE_PROFILE_KEY = 'AgentInstanceProfile'
    AGENT_SECURITY_GROUP_ID_KEY = 'AgentSecurityGroupId'
    MASTER_ID = 'MasterId'
    BASTION_ID = 'BastionId'
    CHECKPOINT_BUCKET = 'CheckpointBucket'
    MASTER_INSTANCE_TYPE = 'MasterInstanceType'
    AGENT_INSTANCE_TYPE = 'AgentInstanceType'
    PUBLIC_IP_ADDRESS = 'PublicIpAddress'
    PRIVATE_IP_ADDRESS = 'PrivateIpAddress'
    SUBNET_ID_KEY = 'SubnetId'


class resources:
    SIMPLE = 'simple.yaml'
    SECURE = 'secure.yaml'
    VPC = 'vpc.yaml'


class master_config:
    # Master Configs
    PROVISIONER = 'provisioner'
    MASTER_URL = 'master_url'
    AGENT_DOCKER_NETWORK = 'agent_docker_network'
    MAX_IDLE_AGENT_PERIOD = 'max_idle_agent_period'
    PROVIDER = 'provider'
    ROOT_VOLUME_SIZE = 'root_volume_size'
    IMAGE_ID = 'image_id'
    TAG_KEY = 'tag_key'
    TAG_VALUE = 'tag_value'
    INSTANCE_NAME = 'instance_name'
    SSH_KEY_NAME = 'ssh_key_name'
    NETWORK_INTERFACE = 'network_interface'
    SECURITY_GROUP_ID = 'security_group_id'
    SUBNET_ID = 'subnet_id'
    INSTANCE_TYPE = 'instance_type'
    IAM_INSTANCE_PROFILE_ARN = 'iam_instance_profile_arn'
    MAX_INSTANCES = 'max_instances'
    PUBLIC_IP = 'public_ip'

    # Default Config Values
    DEFAULT_TAG_KEY = 'pedl'
    DEFAULT_TAG_VALUE = 'pedl-agent'
    DEFAULT_MASTER_URL = 'http://local-ipv4:8080'
    DEFAULT_DOCKER_NETWORK = 'pedl'
    DEFAULT_MAX_IDLE_AGENT_PERIOD = '1m'
    DEFAULT_PROVIDER = 'aws'
    DEFAULT_ROOT_VOLUME_SIZE = 200
    DEFAULT_MAX_INSTANCES = 5
    DEFAULT_INSTANCE_NAME = 'pedl-agent'
    DEFAULT_NETWORK_INTERFACE = {}

    DEFAULT_MASTER_CONFIGS = {
        PROVISIONER: {
            MASTER_URL: DEFAULT_MASTER_URL,
            AGENT_DOCKER_NETWORK: DEFAULT_DOCKER_NETWORK,
            MAX_IDLE_AGENT_PERIOD: DEFAULT_MAX_IDLE_AGENT_PERIOD,
            PROVIDER: DEFAULT_PROVIDER,
            ROOT_VOLUME_SIZE: DEFAULT_ROOT_VOLUME_SIZE,
            MAX_INSTANCES: DEFAULT_MAX_INSTANCES,
            TAG_KEY: DEFAULT_TAG_KEY,
            TAG_VALUE: DEFAULT_TAG_VALUE,
            INSTANCE_NAME: DEFAULT_INSTANCE_NAME,
            NETWORK_INTERFACE: DEFAULT_NETWORK_INTERFACE

        }
    }


class misc:
    PEDL_MASTER_YAML_PATH = '/usr/local/pedl/etc/master.yaml'
    SECURE_SSH_COMMAND = 'ssh -i <pem-file>  ubuntu@{master_ip} -o ' \
                         '"proxycommand ssh -W %h:%p -i <pem-file> ubuntu@{bastion_ip}"'
    SIMPLE_SSH_COMMAND = 'ssh -i <pem-file>  ubuntu@{master_ip}'
    TEMPLATE_PATH = 'pedl_deploy.templates'
