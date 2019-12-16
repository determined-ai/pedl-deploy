# PEDL Deploy

## Install
1. Clone the repository

2. ```commandline
   cd ped-deploy
   pip install .
   ```

## Deploy PEDL to AWS
```commandline
pedl-deploy
```

## Delete PEDL Deployment
```commandline
pedl-deploy --delete
```

## Command Line Arguments
| Argument                 | Description                                           | Default Value     |
|--------------------------|-------------------------------------------------------|-------------------|
| `--delete`               | Flag to trigger stack deletion.                       | `False`           |
| `--deployment-type`      | The type of deployment. See Deployment Types section. | `simple`          |
| `--master-ami`           | The AMI to use for the master instance.               | Latest Master AMI |
| `--agent-ami`            | The AMI to use for the agent instances.               | Latest Agent AMI  |
| `--keypair`              | The keypair for master and agent instances.           | `pedl-keypair`    |
| `--master-instance-type` | The AWS instance type for master instance.            | `t2.medium`       |
| `--agent-instance-type`  | The AWS instance type for the agent instance.         | `p2.8xlarge`      |

## Deployment Types
### Simple
The simple deployment is the easiest way to get a PEDL cluster deployed into AWS. It will create the master instance in the default subnet for the account. 

### Secure
The secure deployment creates resources to lock down PEDL. These resources are:
- A VPC with a public and a private subnet
- A NAT Gateway for the private subnet to make outbound connections
- An S3 VPC Gateway so the private subnet can access S3
- A bastion instance in the public subnet
- A master instance in the private subnet

In this setup, the master and agents will not have public ips, and can only be accessed through the bastion host. The UI is accessed through an ssh tunnel through the bastion to the master.
