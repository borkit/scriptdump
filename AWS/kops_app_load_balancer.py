"""
Kubernetes Cluster: AWS: Application LoadBalancer
"""
# Requirements:
#
# aws configure:
#       AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION

import os
import boto3
import random
import string
import sys, getopt
import json


ec2 = boto3.resource('ec2')


def find_vpc_id(cluster_name):
    client = boto3.client('ec2')
    response = client.describe_vpcs()
    for data in response['Vpcs']:
        for vpc_name in data['Tags']:
            if vpc_name['Value'] == cluster_name:
                return data['VpcId']


def find_all_subnets(cluster_name):
    vpc_id = find_vpc_id(cluster_name)
    vpc = ec2.Vpc(vpc_id)
    subnets = vpc.subnets.all()
    return subnets


def find_target_group_arns(response):
    target_group_arn=json.loads(response)
    for target_group_arn in target_group_arn['TargetGroups']:
        return target_group_arn['TargetGroupArn']


def find_load_balancer_arn(response):
    load_balancers = json.loads(response)
    for load_balancer in load_balancers['LoadBalancers']:
        return load_balancer['LoadBalancerArn']


def find_load_balancer_endpoint(response):
    load_balancers = json.loads(response)
    for load_balancer in load_balancers['LoadBalancers']:
        return load_balancer['DNSName']


def generate_random_name(length):
    return ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(length))


def create_security_group(cluster_name):
    print("Creating security group ... ")
    client = boto3.client('ec2')
    response = client.create_security_group(
        DryRun = False,
        GroupName='k8s-elb-' + generate_random_name(30),
        Description= cluster_name + " Application Loadbalancer",
        VpcId=find_vpc_id(cluster_name)
    )
    print(response)
    return response['GroupId']


# Unable to find security group based on group name in non default vpc
def find_group_id_by_name(groupname):
    iam_ec2_client =  boto3.client('ec2')
    security_group_list = iam_ec2_client.describe_security_groups()
    for security_group in security_group_list['SecurityGroups']:
        if(security_group['GroupName'] == groupname):
            return security_group['GroupId']


def authorize_ingress_sg(port, cidr, security_group_id):
    print("Authorize ingress ...")
    security_group = ec2.SecurityGroup(security_group_id)
    response = security_group.authorize_ingress(
        DryRun=False,
        GroupId=security_group_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': port,
                'ToPort': port,
                'IpRanges': [
                    {
                        'CidrIp': cidr.strip()
                    },
                ]
            },
        ]
    )
    print(response)


def authorize_ingress_sg_v2(port, security_group_id, ip_permission_sg_id):
    print("Authorize ingress new security group to nodes ...")
    security_group = ec2.SecurityGroup(security_group_id)
    response = security_group.authorize_ingress(
        DryRun=False,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': int(port),
                'ToPort': int(port),
                'UserIdGroupPairs': [
                    {
                        'GroupId': ip_permission_sg_id,
                    },
                ]
            },
        ]
    )
    print(response)


def create_load_balancer(cluster_name, security_group):
    authorize_ingress_sg(80, '0.0.0.0/0', security_group)

    print("Creating Load Balancer ...")
    load_balancer_name = generate_random_name(32)

    subnets = ""
    subnet_iterator = find_all_subnets(cluster_name)
    for subnet in subnet_iterator:
        subnets += str(subnet.id + " ")

    command = "aws elbv2 create-load-balancer --name " + load_balancer_name + " --subnets " + subnets + " --security-groups " + security_group
    response = os.popen(command).read()
    print(response)
    return response


def create_target_group(cluster_name, target_group_name, target_port):
    print("Create default target group ...")
    vpc = find_vpc_id(cluster_name)
    command = "aws elbv2 create-target-group --name " + target_group_name + " --protocol HTTP --port " + target_port + " --vpc " + vpc
    response = os.popen(command).read()
    print(response)
    return response


def attach_load_balancer_target_groups(auto_scaling_group_name, target_group_arns):
    print("Attaching target group to load balancer ...")
    command = "aws autoscaling attach-load-balancer-target-groups --auto-scaling-group-name "+ auto_scaling_group_name + " --target-group-arns " + target_group_arns
    response = os.popen(command).read()
    print(response)
    return response


def create_elb_listener(load_balancer_arn, target_group_arns):
    print("Creating default listener ...")
    command = "aws elbv2 create-listener --load-balancer-arn "+ load_balancer_arn + " --protocol HTTP --port 80 --default-actions Type=forward,TargetGroupArn=" + target_group_arns
    response = os.popen(command).read()
    print(response)
    return response


def create_rule(listener_arn, target_group_arn, context, priority):
    print("Creating context rule ...")
    command = "aws elbv2 create-rule --listener-arn " + listener_arn + " --conditions Field=path-pattern,Values='/"+ context + "/*' --priority " + priority + " --actions Type=forward,TargetGroupArn=" + target_group_arn
    response = os.popen(command).read()
    print(response)
    return response


def entrypoint(cluster_name, target_port):
    ip_permission_sg_id = create_security_group(cluster_name)
    load_balancer_response = create_load_balancer(cluster_name, ip_permission_sg_id)
    load_balancer_arn = find_load_balancer_arn(load_balancer_response)
    target_group_arn = find_target_group_arns(create_target_group(cluster_name, generate_random_name(15), target_port))
    attach_load_balancer_target_groups('nodes.'+cluster_name, target_group_arn)
    create_elb_listener(load_balancer_arn, target_group_arn)
    security_group = find_group_id_by_name('nodes.'+cluster_name)
    authorize_ingress_sg_v2(target_port, security_group, ip_permission_sg_id)
    print("End Point Created as: " + find_load_balancer_endpoint(load_balancer_response))


def main(argv):
    help_message = 'python alb.py -c <clustername> -p <targetport>'

    try:
        opts, args = getopt.getopt(argv,"hc:p:", ["clustername=", "targetport="])

        if not opts:
            print help_message

    except getopt.GetoptError:
        print help_message
        sys.exit(2)

    cluster_name = ''
    target_port = ''

    for opt, arg in opts:
        if opt == '-h':
            print help_message
            sys.exit()
        elif opt in ("-c", "--clustername"):
            cluster_name = arg
        elif opt in ("-p", "--targetport"):
            target_port = arg

    if cluster_name != '' and target_port != '':
        entrypoint(cluster_name, target_port)


if __name__ == '__main__':
    main(sys.argv[1:])
