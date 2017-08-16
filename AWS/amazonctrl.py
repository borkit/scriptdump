# -*- coding: utf-8 -*-

"""A simple tool to document how to control AWS resources.

AWS AUTHENTICATION
-------------------

In order to run any of the code below, you need a profile with AWS credentials
set up on your computer. It's very easy to do this. Google how to configure
your profile with boto3, or visit the docs:

    http://boto3.readthedocs.org/en/latest/guide/configuration.html

Note: you need an AWS user with access to everything to run all these
commands. If you see permission denied errors, it's because the user
you're authenticating with does not have access to do what you're code
is trying to do.


SETUP
-----

To try this code out, make sure you have python 3.4+ installed.

Then download this file into a folder (e.g., into "$HOME/amazonctl"). CD into
that folder, create a virtual environment, and activate it::

    > cd $HOME/amazonctl
    > pyvenv venv
    > . venv/bin/activate

On Windows, the above commands will be slightly different, but the steps
are the same: go into the folder, create a virtual environment, then
activate it.

Finally, download the dependencies: boto3, click, and jupyter::

    > pip install boto3 click jupyter


JUPYTER
--------

Jupyter provides an interactive Python console that makes it very easy to
explore Python code/packages.

You can enter the Jupyter Console by typing the command::

    > jupyter console

From there you can import this file::

    >>> import amazonctl

You can then use tab completion after the dot to see possible options::

    >>> amazonctl.<hit Tab>

To see the code's documentation, add a question mark after a function
and hit <Enter>::

    >>> amazonctl.create_vpc?<hit Enter>

You can do similar things with boto3 to explore AWS. In the Jupyter console,
import boto3::

    >>> import boto3

Then explore the boto3 interface. The ``?`` functionality of Jupyter is
extremely helpful. Boto3's documentation is outstanding..

"""

import json

import boto3
import click


def get_client(service):
    """Get an AWS client for a service."""
    session = boto3.Session()
    return session.client(service)



"""#########################################################################

VPCs and Subnets
----------------

To see all VPCs::

    >>> amazonctl.get_vpcs()

To create a VPC, give it a CIDR block::

    >>> amazonctl.create_vpc("192.168.0.0/24")

To see all VPCs::

    >>>> amazonctl.get_vpcs()

To delete a VPC, you need its VPC ID (which you can get from the
``get_vpcs()`` function.::

    >>> amazonctl.delete_vpc("vpc-9fe44ffb")

To create a subnet in a VPC::

    >>> amazonctl.create_subnet("vpc-9fe44ffb", "192.168.0.10/24")

To see all subnets::

    >>> amazonctl.get_subnets()

To delete a subnet from a VPC, use its Subnet ID (which you can get from
the ``get_subnets()`` function.::

    >>> amazonctl.delete_subnet("subnet-8924feb4")

"""


def create_vpc(cidr_block):
    """Create a VPC."""
    client = get_client("ec2")
    params = {}
    params["CidrBlock"] = cidr_block
    return client.create_vpc(**params)


def delete_vpc(vpc_id):
    """Delete a VPC."""
    client = get_client("ec2")
    params = {}
    params["VpcId"] = vpc_id
    return client.delete_vpc(**params)

def get_vpcs():
    """List info about all VPCs."""
    client = get_client("ec2")
    return client.describe_vpcs()


def create_subnet(vpc_id, cidr_block):
    """Create a subnet in a VPC."""
    client = get_client("ec2")
    params = {}
    params["VpcId"] = vpc_id
    params["CidrBlock"] = cidr_block
    return client.create_subnet(**params)


def delete_subnet(subnet_id):
    """Delete a subnet from a VPC."""
    client = get_client("ec2")
    params = {}
    params["SubnetId"] = subnet_id
    return client.delete_subnet(**params)


def get_subnets():
    """List info about all subnets."""
    client = get_client("ec2")
    return client.describe_subnets()



"""#########################################################################

Security Groups, Keys, and Network ACLs
---------------------------------------

To create a security group::

    >>> amazonctl.create_security_group("my-security-group", "vpc-9fe44ffb")

To add an inbound (ingress) rule, e.g. accept requests from port 80 to port 80
from anywhere::

    >>> amazonctl.create_ingress_rule("sg-0fea4969", "tcp", 80, 80, "0.0.0.0/0")

To delete that inbound (ingress) rule::

    >>> amazonctl.delete_ingress_rule("sg-0fea4969", "tcp", 80, 80, "0.0.0.0/0")

The same applies to creating and deleting outbound (egress) rules:

    >>> amazonctl.create_egress_rule("sg-0fea4969", "tcp", 80, 80, "0.0.0.0/0")
    >>> amazonctl.delete_egress_rule("sg-0fea4969", "tcp", 80, 80, "0.0.0.0/0")

Note that defining security group ingress/egress rules like this are limited
to VPCs. EC2 classic does it differently.

To view all security groups::

    >>> amazonctl.get_security_groups()

To delete a security group, use the security group ID (which you can get
from the ``get_security_groups()`` function)::

    >>> amazonctl.delete_security_group("sg-0fea4969")

To create a new key pair::

    >>> amazonctl.create_key_pair("my-keypair")

To delete a key pairs::

    >>> amazonctl.delete_key_pair("my-keypair")

To see all key pairs::

    >>> amazonctl.get_key_pairs()

To create a network ACL in a VPC::

    >>> amazonctl.create_network_acl("pc-9fe44ffb")

To see all network ACLs::

    >>> amazonctl.get_network_acls()

To delete a network ACL, use its ACL ID (which you can get from the
``get_network_acls()`` function)::

    >>> amazonctl.delete_network_acl("acl-ae3283ca")

To add an ACL entry that allows certain inbound traffic::

    >>> amazonctl.create_network_acl_ingress_entry("acl-ae3283ca",
    ..:     rule_num=150, protocol="6", cidr_block="0.0.0.0/0",
    ..:     from_port=80, to_port=80, allow=True)

To update that rule::

    >>> amazonctl.update_network_acl_ingress_entry("acl-ae3283ca",
    ..:     rule_num=150, protocol="6", cidr_block="192.168.10.10/24",
    .. :    from_port=80, to_port=80, allow=True)

To delete that rule, use the ACL ID and the rule number::

    >>> amazonctl.delete_network_acl_ingress_entry("acl-ae3283ca", 150)

For outbound rules, it's similar, just use ``egress`` in function calls
instead of ``ingress``, for instance ``create_network_acl_egress_entry()``.

To change a subnet from one ACL to another, use the association ID of the
subet (which you can get from the ``get_network_acls()`` function), and just
point that at a different ACL::

    >>> amazonctl.replace_network_acl_association("acl-ae3283ca",
    ..:     "aclassoc-a7dad2c1")

Route Table commands could be put in here too.

"""


def create_security_group(name, vpc_id):
    """Create a security group."""
    client = get_client("ec2")
    params = {}
    params["GroupName"] = name
    params["Description"] = name + " security group for " + vpc_id
    params["VpcId"] = vpc_id
    return client.create_security_group(**params)


def create_ingress_rule(security_group_id, protocol, from_port, to_port, cidr_block):
    """Create a security group ingress rule."""
    client = get_client("ec2")
    params = {}
    params["GroupId"] = security_group_id
    params["IpPermissions"] = [{
        "IpProtocol": protocol,
        "FromPort": from_port,
        "ToPort": to_port,
        "IpRanges": [{"CidrIp": cidr_block}],
        }]
    return client.authorize_security_group_ingress(**params)


def delete_ingress_rule(security_group_id, protocol, from_port, to_port, cidr_block):
    """Delete a security group ingress rule."""
    client = get_client("ec2")
    params = {}
    params["GroupId"] = security_group_id
    params["IpPermissions"] = [{
        "IpProtocol": protocol,
        "FromPort": from_port,
        "ToPort": to_port,
        "IpRanges": [{"CidrIp": cidr_block}],
        }]
    return client.revoke_security_group_ingress(**params)


def create_egress_rule(security_group_id, protocol, from_port, to_port, cidr_block):
    """Create a security group egress rule."""
    client = get_client("ec2")
    params = {}
    params["GroupId"] = security_group_id
    params["IpPermissions"] = [{
        "IpProtocol": protocol,
        "FromPort": from_port,
        "ToPort": to_port,
        "IpRanges": [{"CidrIp": cidr_block}],
        }]
    return client.authorize_security_group_egress(**params)


def delete_egress_rule(security_group_id, protocol, from_port, to_port, cidr_block):
    """Delete a security group egress rule."""
    client = get_client("ec2")
    params = {}
    params["GroupId"] = security_group_id
    params["IpPermissions"] = [{
        "IpProtocol": protocol,
        "FromPort": from_port,
        "ToPort": to_port,
        "IpRanges": [{"CidrIp": cidr_block}],
        }]
    return client.revoke_security_group_egress(**params)


def get_security_groups():
    """List info about all security groups."""
    client = get_client("ec2")
    return client.describe_security_groups()


def delete_security_group(security_group_id):
    """Delete a security group."""
    client = get_client("ec2")
    params = {}
    params["GroupId"] = security_group_id
    return client.delete_security_group(**params)


def create_key_pair(name):
    """Create a key pair."""
    client = get_client("ec2")
    params = {}
    params["KeyName"] = name
    return client.create_key_pair(**params)


def delete_key_pair(name):
    """Delete a key pair."""
    client = get_client("ec2")
    params = {}
    params["KeyName"] = name
    return client.delete_key_pair(**params)


def get_key_pairs():
    """List info about all key pairs."""
    client = get_client("ec2")
    return client.describe_key_pairs()


def create_network_acl(vpc_id):
    """Create a network ACL."""
    client = get_client("ec2")
    params = {}
    params["VpcId"] = vpc_id
    return client.create_network_acl(**params)


def delete_network_acl(acl_id):
    """Delete a network ACL."""
    client = get_client("ec2")
    params = {}
    params["NetworkAclId"] = acl_id
    return client.delete_network_acl(**params)


def get_network_acls():
    """List info about all network ACLs."""
    client = get_client("ec2")
    return client.describe_network_acls()


def create_network_acl_ingress_entry(acl_id, rule_num, protocol, cidr_block,
                                     from_port, to_port, allow=True):
    """Create an ACL entry for inbound traffic.

    Note that ``protocol`` should be an IP Protocol number, but passed in
    as a string, like "6", not 6 or "tcp"."""
    client = get_client("ec2")
    params = {}
    params["NetworkAclId"] = acl_id
    params["RuleNumber"] = rule_num
    params["Protocol"] = protocol
    params["CidrBlock"] = cidr_block
    params["Egress"] = False
    params["RuleAction"] = "ALLOW" if allow else "DENY"
    params["PortRange"] = {"From": from_port, "To": to_port}
    return client.create_network_acl_entry(**params)


def update_network_acl_ingress_entry(acl_id, rule_num, protocol, cidr_block,
                                     from_port, to_port, allow=True):
    """Update an ACL entry for inbound traffic.

    Note that ``protocol`` should be an IP Protocol number, but passed in
    as a string, like "6", not 6 or "tcp"."""
    client = get_client("ec2")
    params = {}
    params["NetworkAclId"] = acl_id
    params["RuleNumber"] = rule_num
    params["Protocol"] = protocol
    params["CidrBlock"] = cidr_block
    params["Egress"] = False
    params["RuleAction"] = "ALLOW" if allow else "DENY"
    params["PortRange"] = {"From": from_port, "To": to_port}
    return client.replace_network_acl_entry(**params)


def delete_network_acl_ingress_entry(acl_id, rule_num):
    """Delete an ACL entry for inbound traffic."""
    client = get_client("ec2")
    params = {}
    params["NetworkAclId"] = acl_id
    params["RuleNumber"] = rule_num
    params["Egress"] = False
    return client.delete_network_acl_entry(**params)


def create_network_acl_egress_entry(acl_id, rule_num, protocol, cidr_block,
                                     from_port, to_port, allow=True):
    """Create an ACL entry for outbound traffic.

    Note that ``protocol`` should be an IP Protocol number, but passed in
    as a string, like "6", not 6 or "tcp"."""
    client = get_client("ec2")
    params = {}
    params["NetworkAclId"] = acl_id
    params["RuleNumber"] = rule_num
    params["Protocol"] = protocol
    params["CidrBlock"] = cidr_block
    params["Egress"] = True
    params["RuleAction"] = "ALLOW" if allow else "DENY"
    params["PortRange"] = {"From": from_port, "To": to_port}
    return client.create_network_acl_entry(**params)


def update_network_acl_egress_entry(acl_id, rule_num, protocol, cidr_block,
                                     from_port, to_port, allow=True):
    """Update an ACL entry for outbound traffic.

    Note that ``protocol`` should be an IP Protocol number, but passed in
    as a string, like "6", not 6 or "tcp"."""
    client = get_client("ec2")
    params = {}
    params["NetworkAclId"] = acl_id
    params["RuleNumber"] = rule_num
    params["Protocol"] = protocol
    params["CidrBlock"] = cidr_block
    params["Egress"] = False
    params["RuleAction"] = "ALLOW" if allow else "DENY"
    params["PortRange"] = {"From": from_port, "To": to_port}
    return client.replace_network_acl_entry(**params)


def delete_network_acl_egress_entry(acl_id, rule_num):
    """Delete an ACL entry for outbound traffic."""
    client = get_client("ec2")
    params = {}
    params["NetworkAclId"] = acl_id
    params["RuleNumber"] = rule_num
    params["Egress"] = True
    return client.delete_network_acl_entry(**params)


def change_network_acl_association(acl_id, assoc_id):
    """Change an ACL's association."""
    client = get_client("ec2")
    params = {}
    params["AssociationId"] = assoc_id
    params["NetworkAclId"] = acl_id
    return client.replace_network_acl_association(**params)



"""#########################################################################

Auto Scaling Groups and Launch Configurations
---------------------------------------------

To create a launch configuration::

    >>> amazonctl.create_launch_configuration("my-launch-config",
    ..:     "ami-c16422a4", key_pair="my-key-pair",
    ..:     security_groups=["sg-0fea4969"],
    ..:     instance_type="t2.medium")

To delete a launch configuration::

    >>> amazonctl.delete_launch_configuration("my-launch-config")


To see all launch configurations::

    >>> amazonctl.get_launch_configurations()

To create an auto scaling group from a launch configuration::

    >>> amazonctl.create_auto_scaling_group("my-asg", "my-launch-config",
    ..:     min_size=1, max_size=4, desired_size=1,
    ..:     subnets=["subnet-8924feb4"])

To see all auto scaling groups::

    >>> amazonctl.get_auto_scaling_groups()

To delete an auto scaling group::

    >>> amazonctl.delete_auto_scaling_group("my-asg")

Note: if you want to use an auto scaling group with a cluster, tell the
launch config which cluster to use, e.g.,::

    >>> amazonctl.create_launch_configuration("my-launch-config",
    ..:     "ami-c16422a4", ..., cluster="my-cluster")

Currently, AWS tells instances which cluster they should launch into by
including a bash script in the user data. That script is encoded in
the ``create_launch_configuration()`` function.

"""


def create_launch_configuration(name, ami_id, key_pair=None,
                                security_groups=None,
                                instance_type="t2.micro", public_ip=True,
                                user_data=None, cluster=None):
    """Create a launch configuration."""
    client = get_client("autoscaling")
    params = {}
    params["LaunchConfigurationName"] = name
    params["ImageId"] = ami_id
    params["InstanceType"] = instance_type
    if key_pair:
        params["KeyName"] = key_pair
    if security_groups:
        params["SecurityGroups"] = security_groups
    if public_ip:
        params["AssociatePublicIpAddress"] = True
    if cluster:
        params["UserData"] = "#!/bin/bash\n" \
                             + "echo ECS_CLUSTER=" \
                             + name \
                             + " >> /etc/ecs/ecs.config"
    elif user_data:
        params["UserData"] = user_data
    return client.create_launch_configuration(**params)


def delete_launch_configuration(name):
    """Delete a launch cofiguration."""
    client = get_client("autoscaling")
    params = {}
    params["LaunchConfigurationName"] = name
    return client.delete_launch_configuration(**params)


def get_launch_configurations():
    """List info about all launch configurations."""
    client = get_client("autoscaling")
    return client.describe_launch_configurations()


def create_auto_scaling_group(name, launch_configuration, min_size=1,
                              max_size=1, desired_size=1, subnets=None):
    """Create an auto scaling group."""
    client = get_client("autoscaling")
    params = {}
    params["AutoScalingGroupName"] = name
    params["LaunchConfigurationName"] = launch_configuration
    params["MinSize"] = min_size
    params["MaxSize"] = max_size
    params["DesiredCapacity"] = desired_size
    if subnets:
        params["VPCZoneIdentifier"] = ",".join(subnets)
    return client.create_auto_scaling_group(**params)


def delete_auto_scaling_group(name, force=True):
    """Delete an auto scaling group."""
    client = get_client("autoscaling")
    params = {}
    params["AutoScalingGroupName"] = name
    params["ForceDelete"] = force
    return client.delete_auto_scaling_group(**params)


def get_auto_scaling_groups():
    """List info about all auto scaling groups."""
    client = get_client("autoscaling")
    return client.describe_auto_scaling_groups()



"""#########################################################################

Load Balancers
--------------

To create an elastic load balancer::

    >>> amazonctl.create_load_balancer("my-elb", "http", 80, 80,
    ..:     subnets=["subnet-8924feb4"], security_groups=["sg-0fea4969"],
    ..:     private=True)

To list all load balancers::

    >>> amazonctl.get_load_balancers()

To delete a load balancer::

    >>> amazonctl.delete_load_balancer("my-elb")

To attach a load balancer to an auto scaling group::

    >>> amazonctl.attach_load_balancer("my-asg", "my-elb")

And to detach it:

    >>> amazonctl.detach_load_balancer("my-asg", "my-elb")

"""


def create_load_balancer(name, protocol, elb_port, instance_port,
                         ssl_cert=None, subnets=None, security_groups=None,
                         private=False):
    """Create a load balancer."""
    client = get_client("elb")
    params = {}
    params["LoadBalancerName"] = name
    listener = {
        "Protocol": protocol,
        "LoadBalancerPort": elb_port,
        "InstancePort": instance_port
        }
    if ssl_cert:
        listener["SSLCertificateId"] = ssl_cert
    params["Listeners"] = [listener]
    if subnets:
        params["Subnets"] = subnets
    if security_groups:
        params["SecurityGroups"] = security_groups
    if private:
        params["Scheme"] = "internal"
    return client.create_load_balancer(**params)

def delete_load_balancer(name):
    """Delete a load balancer."""
    client = get_client("elb")
    params = {}
    params["LoadBalancerName"] = name
    return client.delete_load_balancer(**params)


def get_load_balancers():
    """List info about all load balancers."""
    client = get_client("elb")
    return client.describe_load_balancers()


def attach_load_balancer(group_name, load_balancer_name):
    """Attach a load balancer to an auto scaling group."""
    client = get_client("autoscaling")
    params = {}
    params["AutoScalingGroupName"] = group_name
    params["LoadBalancerNames"] = [load_balancer_name]
    return client.attach_load_balancers(**params)


def detach_load_balancer(group_name, load_balancer_name):
    """Detach a load balancer from an auto scaling group."""
    client = get_client("autoscaling")
    params = {}
    params["AutoScalingGroupName"] = group_name
    params["LoadBalancerNames"] = [load_balancer_name]
    return client.detach_load_balancers(**params)



"""#########################################################################

Cloud Formation
---------------

Suppose you have a simple template at my-stack.template:

    {
      "AWSTemplateFormatVersion": "2010-09-09",
      "Resources": {
        "BasicLaunchConfig": {
          "Type": "AWS::AutoScaling::LaunchConfiguration",
          "Properties": {
            "ImageId": "ami-e3106686",
            "InstanceType": "t2.micro",
          }
        }
      }
    }

To create a Cloud Formation stack from that template::

    >>> amazonctl.create_stack("my-stack", template="my-stack.template")

To list all stacks::

    >>> amazonctl.get_stacks()

To delete a stack::

    >>> amazonctl.delete_stack("my-stack")

"""

def create_stack(name, template, parameters=None):
    """Create a Cloud Formation stack.

    Note: the parameters should follow the AWS format:
    [{ "ParameterKey": "<key>", "ParameterValue": "<value>"}, ... ]

    """
    client = get_client("cloudformation")
    params = {}
    params["StackName"] = name
    params["Capabilities"] = ["CAPABILITY_IAM"]
    with open(template) as template_file:
        contents = template_file.read()
        params["TemplateBody"] = contents
    if parameters:
        params["Parameters"] = parameters
    return client.create_stack(**params)


def delete_stack(name):
    """Delete a Cloud Formation stack."""
    client = get_client("cloudformation")
    params = {}
    params["StackName"] = name
    return client.delete_stack(**params)


def get_stacks():
    """List info about all stacks."""
    client = get_client("cloudformation")
    return client.describe_stacks()



"""#########################################################################

Container Service
-----------------

To create a cluster::

    >>> amazonctl.create_cluster("my-cluster")

To delete a cluster::

    >>> amazonctl.delete_cluster("my-cluster")

To get a list of cluster ARNs::

    >>> data = amazonctl.get_cluster_arns()

To get info about those clusters::

    >>> cluster_arns = data.get("clusterArns")
    >>> amazonctl.get_clusters(cluster_arns)

To get a list of container instance ARNs::

    >>> data = amazonctl.get_container_instance_arns("my-cluster")

To get info about those instances::

    >>> instances = data.get("containerInstanceArns")
    >>> amazonctl.get_container_instances("my-cluster", instances)

You'll need to wait until container instances terminate before you
can delete a cluster. If you need to do that, this call blocks
until the instances are terminated::

    >>> amazonctl.wait_for_instances_to_terminate(instances)

Suppose you have a task definition file called "demo.json" that looks
something like this::

{
    "family": "demo",
    "containerDefinitions": [
        {
            "name": "simpleton",
            "image": "jtpaasch/simpleton:latest",
            "memory": 100,
            "portMappings": [
                {
                    "containerPort": 80,
                    "hostPort": 80
                }
            ],
            "environment": [
                {
                    "name": "FOO",
                    "value": "bar"
                }
            ]
        }
    ],
    "volumes": []
}

You can create a task definition from that::

    >>> amazonctl.create_task_definition("demo.json")

To see all task definition ARNS::

    >>> amazonctl.get_task_definition_arns()

To get info about a task definition, use the "family" specified in
the task definition's json file::

    >>> amazonctl.get_task_definition("my-task-definition")

To delete a task definition, use it's family name and revision number::

    >>> amazonctl.delete_task_definition("my-task-definition:1")

To get a list of task ARNs in a cluster::

    >>> data = amazonctl.get_task_arns("my-cluster")

To get info about those tasks:

    >>> task_arns = data.get("taskArns")
    >>> amazonctl.get_tasks("my-cluster", task_arns)

To run a task in a cluster::

    >>> amazonctl.run_task("my-cluster", "my-task-definition")

To stop the task, use the task ID (which you can get from ``get_tasks()``)::

    >>> amazonctl.stop_task("my-cluster", "A4503-...")

To get a list of service ARNs in a cluster::

    >>> data = amazonctl.get_service_arns("my-cluster")

To get info about those services::

    >>> service_arns = data.get("serviceArns")
    >>> amazonctl.get_services("my-cluster", service_arns)

To create a service, do something like this::

    >>> amazonctl.create_service("my-service", "my-cluster",
    ..:     "my-task-definition", count=3,
    ..:     load_balancer="my-elb", role="EcsServiceRole")

To update the service (either the count or the task definition)::

    >>> amazonctl.update_service("my-service", "my-cluster", count=5)

To delete a service from a cluster::

    >>> amazonctl.delete_service("my-service", "my-cluster")

"""


def create_cluster(name):
    """Create an ECS cluster."""
    client = get_client("ecs")
    params = {}
    params["clusterName"] = name
    return client.create_cluster(**params)


def delete_cluster(name):
    """Delete an ECS cluster."""
    client = get_client("ecs")
    params = {}
    params["cluster"] = name
    return client.delete_cluster(**params)


def get_cluster_arns():
    """List all cluster ARNs."""
    client = get_client("ecs")
    return client.list_clusters()


def get_clusters(clusters):
    """List info about the specified clusters."""
    client = get_client("ecs")
    params = {}
    params["clusters"] = clusters
    return client.describe_clusters(**params)


def get_container_instance_arns(cluster):
    """List all container instance ARNs."""
    client = get_client("ecs")
    return client.list_container_instances()


def get_container_instances(cluster, instances):
    """List info about the container instances in a cluster."""
    client = get_client("ecs")
    params = {}
    params["cluster"] = cluster
    params["containerInstances"] = instances
    return client.describe_container_instances(**params)


def create_task_definition(json_file):
    """Create an ECS task definition."""
    client = get_client("ecs")
    params = {}
    with open(json_file) as f:
        data = json.load(f)
    params["family"] = data.get("family")
    params["containerDefinitions"] = data.get("containerDefinitions")
    params["volumes"] = data.get("volumes")
    return client.register_task_definition(**params)


def get_task_definition_arns():
    """List all task definition ARNs."""
    client = get_client("ecs")
    return client.list_task_definitions()


def get_task_definition(task_definition):
    """List info about the specified task definition."""
    client = get_client("ecs")
    params = {}
    params["taskDefinition"] = task_definition
    return client.describe_task_definition(**params)


def delete_task_definition(name):
    """Delete an ECS task definition.

    Note: The whole name is needed, i.e., family and revision.

    """
    client = get_client("ecs")
    params = {}
    params["taskDefinition"] = name
    return client.deregister_task_definition(**params)


def get_task_arns(cluster):
    """List all task ARNs for a cluster."""
    client = get_client("ecs")
    params = {}
    params["cluster"] = cluster
    return client.list_tasks(**params)


def get_tasks(cluster, tasks):
    """Get info about the tasks in a cluster."""
    client = get_client("ecs")
    params = {}
    params["cluster"] = cluster
    params["tasks"] = tasks
    return client.describe_tasks(**params)


def run_task(cluster, task_definition):
    """Run a task in a cluster."""
    client = get_client("ecs")
    params = {}
    params["cluster"] = cluster
    params["taskDefinition"] = task_definition
    return client.run_task(**params)


def stop_task(cluster, task_id):
    """Stop a task in a cluster."""
    client = get_client("ecs")
    params = {}
    params["cluster"] = cluster
    params["task"] = task_id
    return client.stop_task(**params)


def get_service_arns(cluster):
    """List all service ARNs for a cluster."""
    client = get_client("ecs")
    params = {}
    params["cluster"] = cluster
    return client.list_services(**params)


def get_services(cluster, services):
    """Get info about the services in a cluster."""
    client = get_client("ecs")
    params = {}
    params["cluster"] = cluster
    params["services"] = services
    return client.describe_services(**params)


def create_service(name, cluster, task_definition, count=1,
                   load_balancer=None, role=None):
    """Create a service in a cluster."""
    client = get_client("ecs")
    params = {}
    params["serviceName"] = name
    params["taskDefinition"] = task_definition
    params["cluster"] = cluster
    params["desiredCount"] = count
    if load_balancer:
        params["loadBalancers"] = [load_balancer]
    if role:
        params["role"] = role
    return client.create_service(**params)


def delete_service(name, cluster):
    """Delete a service in a cluster."""
    client = get_client("ecs")
    params = {}
    params["service"] = name
    params["cluster"] = cluster
    return client.delete_service(**params)


def update_service(name, cluster, task_definition=None, count=None):
    """Update the task count of a service, or the task definition."""
    client = get_client("ecs")
    params = {}
    params["service"] = name
    params["cluster"] = cluster
    if task_definition:
        params["taskDefinition"] = task_definition
    if count:
        params["desiredCount"] = count
    return client.update_service(**params)


def wait_for_instances_to_terminate(instance_ids):
    """Block until EC2 instances terminate."""
    client = get_client("ec2")
    waiter = client.get_waiter("instance_terminated")
    waiter.config.max_attempts = 15
    waiter.wait(InstanceIds=instance_ids)


"""#########################################################################

Elastic Beanstalk
-----------------

To create an S3 bucket to store your applications::

    >>> amazonctl.create_eb_bucket()

To create an application::

    >>> amazonctl.create_application("my-app")

To see info about all applications::

    >>> amazonctl.get_applications()

To delete an application::

    >>> amazonctl.delete_application("my-app")

To see a list of all solutions tacks::

    >>> amazonctl.get_solution_stacks()

To get just the Multi-Container Docker stack::

    >>> amazonctl.get_multicontainer_docker_solution_stack()

To create an environment::

    >>> amazonctl.create_environment("my-env", "my-app", key_pair="my-key-pair",
    ..:     role="EcsServiceRole", profile="IamInstanceProfile")

To get info about all environments::

    >>> amazonctl.get_environments()

To delete an environment::

    >>> amazonctl.delete_environment("my-env")

To upload an application version zip::

    >>> amazonctl.upload_application_version("v1.5.0.zip", "my-eb-bucket",
    ..:     "v1.5.0.zip")

To create a new application version::

    >>> amazonctl.create_application_version("v1.5.0", "my-app",
    ..:     "my-eb-bucket", "v1.5.0.zip")

To get info about all application versions::

    >>> amazonctl.get_application_versions("my-app")

To delete an application version::

    >>> amazonctl.delete_application_version("v1.5.0", "my-app")

"""


def create_application(name):
    """Create an Elastic Beanstalk application."""
    client = get_client("elasticbeanstalk")
    params = {}
    params["ApplicationName"] = name
    return client.create_application(**params)


def delete_application(name, force=True):
    """Delete an Elastic Beanstalk application."""
    client = get_client("elasticbeanstalk")
    params = {}
    params["ApplicationName"] = name
    if force:
        params["TerminateEnvByForce"] = True
    return client.delete_applications(**params)


def get_applications():
    """List info about all Elastic Beanstalk applications."""
    client = get_client("elasticbeanstalk")
    return client.describe_applications()


def get_solution_stacks():
    """Get a list of all available solution stacks."""
    client = get_client("elasticbeanstalk")
    return client.list_available_solution_stacks()


def get_multicontainer_docker_solution_stack():
    """Get the Multi-Container Docker solution stack."""
    response = get_solution_stacks()
    stacks = response.get("SolutionStacks")
    match = "Multi-container Docker 1.7.1"
    items_with_match = (x for x in stacks if match in x)
    return next(items_with_match, None)


def create_environment(name, application, cname=None, tier="web",
                       key_pair=None, instance_type="t2.micro",
                       profile=None, role=None, healthcheck_url=None):
    """Create an Elastic Beanstalk environment.

    Note: you can add OptionsToRemove, just like OptionSettings. Those
    delete defaults that are pre-set.

    """
    client = get_client("elasticbeanstalk")
    params = {}
    params["ApplicationName"] = application
    params["EnvironmentName"] = name
    if not cname:
        cname = application
    params["CNAMEPrefix"] = cname
    if tier == "web":
        tier_definition = {
            "Name": "WebServer",
            "Type": "Standard",
            "Version": "1.0",
            }
    elif tier == "worker":
        tier_definition = {
            "Name": "Worker",
            "Type": "SQS/HTTP",
            "Version": "1.0",
            }
    if tier_definition:
        params["Tier"] = tier_definition
    stack = get_multicontainer_docker_solution_stack()
    params["SolutionStackName"] = stack
    options = []
    if key_pair:
        key_pair_option = {
            "ResourceName": "InstanceType",
            "Namespace": "aws:autoscaling:launchconfiguration",
            "OptionName": "EC2KeyName",
            "Value": key_pair,
            }
        options.append(key_pair_option)
    if instance_type:
        instance_type_option = {
            "ResourceName": "InstanceType",
            "Namespace": "aws:autoscaling:launchconfiguration",
            "OptionName": "InstanceType",
            "Value": instance_type,
            }
        options.append(instance_type_option)
    if profile:
        profile_option = {
            "ResourceName": "IamInstanceProfile",
            "Namespace": "aws:autoscaling:launchconfiguration",
            "OptionName": "IamInstanceProfile",
            "Value": profile,
            }
        options.append(profile_option)
    if role:
        role_option = {
            "ResourceName": "ServiceRole",
            "Namespace": "aws:elasticbeanstalk:environment",
            "OptionName": "ServiceRole",
            "Value": role,
            }
        options.append(role_option)
    if healthcheck_url:
        healthcheck_url_option = {
            "ResourceName": "HealthcheckURL",
            "Namespace": "elasticbeanstalk:application",
            "OptionName": "Application Healthcheck URL",
            "Value": healthcheck_url,
            }
        options.append(healthcheck_url_option)
    if options:
        params["OptionSettings"] = options
    return client.create_environment(**params)


def delete_environment(name, force=True):
    """Delete an Elatic Beanstalk environment."""
    client = get_client("elasticbeanstalk")
    params = {}
    params["EnvironmentName"] = name
    if force:
        params["TerminateResources"] = True
    return client.terminate_environment(**params)


def get_environments():
    """List info about all environments."""
    client = get_client("elasticbeanstalk")
    return client.describe_environments()


def create_eb_bucket():
    """Create an S3 bucket to store application versions in."""
    client = get_client("elasticbeanstalk")
    return client.create_storage_location()


def create_application_version(name, application, s3bucket, s3key):
    """Create a new version of the application."""
    client = get_client("elasticbeanstalk")
    params = {}
    params["ApplicationName"] = application
    params["VersionLabel"] = name
    params["SourceBundle"] = {
        "S3Bucket": s3bucket,
        "S3Key": s3key,
        }
    return client.create_application_version(**params)


def delete_application_version(name, application, delete_bundle=True):
    """Delete a version of the application."""
    client = get_client("elasticbeanstalk")
    params = {}
    params["ApplicationName"] = application
    params["VersionLabel"] = name
    if delete_bundle:
        params["DeleteSourceBundle"] = True
    return client.delete_application_version(**params)


def get_application_versions(application):
    """List info about all versions of an application."""
    client = get_client("elasticbeanstalk")
    params = {}
    params["ApplicationName"] = application
    return client.describe_application_versions(**params)


def upload_application_version(zip_file, s3bucket, s3key):
    """Upload an application version zip to S3."""
    with open(zipfile, "rb") as f:
        data = f.read()
    client = get_client("s3")
    params = {}
    params["Body"] = data
    params["Bucket"] = s3bucket
    params["Key"] = s3key
    return client.put_object(**params)
