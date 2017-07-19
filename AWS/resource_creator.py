# Python script to add new VPC and Launch EC2 instance
# Uses Boto3 for AWS actions
# Author: Laurence Davenport
# Version: 1.0
# Date: 11.11.2015

import re
import boto3
ec2 = boto3.resource('ec2')
client = boto3.client('ec2')

# function to display items in a list - thanks to Said Ali Samed for this
def display_list(items, key_one, key_two=None, key_three=None):
    if type(items) is not list: return
    for item in items:
        print('%i. %s  %s %s' % (items.index(item) + 1, item[key_one], item[key_two] if key_two else '',
                                 item[key_three] if key_three else ''))

#creating list of all available keypairs
keys = client.describe_key_pairs()
key_list = keys['KeyPairs']

# populating the default keypair value with the first in the list
for item in key_list:
    index = key_list.index(item)
    if index == 0:
        default_key = item['KeyName']
        break

# set the bootstrap script for the instance
user_data = '#!/bin/sh\n yum -y install httpd php mysql php-mysql\n chkconfig httpd on\n /etc/init.d/httpd start'

#Gather data from user
happiness = "N"
while happiness != "Y":
    vpc_cidr_block =  input("Please enter VPC CIDR block [10.0.0.0/16]: ") or "10.0.0.0/16"
    subnet_cidr_block =  input("Please enter Subnet CIDR block [10.0.0.0/25]: ") or "10.0.0.0/25"
    print ("KeyPairs that are available to use are:")
    display_list(key_list, 'KeyName')
    key_name = input("Please enter name of keypair [" + default_key + "]: ") or default_key
    secgrp_name = input("Please enter name of Security Group name [sandboxSecGrp]: ") or "sandboxSecGrp"
    secgrp_desc = input("Please enter name of Security Group description [Sandbox security group]: ") or "Sandbox security group"
    ami_name = input("Please enter Instance AMI [ami-bff32ccc]: ") or "ami-bff32ccc"
    intance_type = input("Please enter Instance type [t2.micro]: ") or "t2.micro"

    print ("=====================================")
    print ("======== Values are set to ==========")
    print ("=====================================")
    print ("VPC CIDR block is: " + vpc_cidr_block)
    print ("Subnet CIDR block is: " + subnet_cidr_block)
    print ("Keypair name is: " + key_name)
    print ("Security group name is: " + secgrp_name)
    print ("Security group description is: " + secgrp_desc)
    print ("Instance AMI is: " + ami_name)
    print ("Instance type is: " + intance_type)
    print ("=====================================")

    happiness = input("Are you happy with all these settings [Y/N]: ") or "Y"

# Create step counter
step_no = 1

# Creating the VPC
vpc = ec2.create_vpc(CidrBlock=vpc_cidr_block)
print ("STEP "+  str(step_no) + " - VPC ID: " + vpc.id)
client.modify_vpc_attribute(VpcId=vpc.id, EnableDnsHostnames={"Value": True})

step_no += 1

# create subnet
subnet = vpc.create_subnet(CidrBlock=subnet_cidr_block)
print ("STEP "+  str(step_no) + " - subnet ID: " + subnet.id)
subnet.meta.client.modify_subnet_attribute(SubnetId=subnet.id, MapPublicIpOnLaunch={"Value": True})

step_no += 1

# create internet gateway
gateway = ec2.create_internet_gateway()
print ("STEP "+  str(step_no) + " - Internet Gateway ID: " + gateway.id)

step_no += 1

# attach internet gateway
gateway.attach_to_vpc(VpcId=vpc.id)
print ("STEP "+  str(step_no) + " - Attach Internet Gateway to VPC ")

step_no += 1

# Create route for vpc to internet
route_table = list(vpc.route_tables.all())[0] # get the route table id
client.create_route(RouteTableId=route_table.id,DestinationCidrBlock='0.0.0.0/0',GatewayId=gateway.id)
print ("STEP "+  str(step_no) + " - Add route to internet to routing table: " + route_table.id)

step_no += 1

# create security group
security_group = vpc.create_security_group(GroupName=secgrp_name,Description=secgrp_desc)
print ("STEP "+  str(step_no) + " - Creating security group: " + security_group.id)

step_no += 1

# allow access for SSH
security_group.authorize_ingress(IpProtocol="tcp",CidrIp="0.0.0.0/0",FromPort=22,ToPort=22)
print ("STEP "+  str(step_no) + " - Open port 22 in security group: " + security_group.id)
step_no += 1

# allow access for HTTP
security_group.authorize_ingress(IpProtocol="tcp",CidrIp="0.0.0.0/0",FromPort=80,ToPort=80)
print ("STEP "+  str(step_no) + " - Open port 80 in security group: " + security_group.id)
step_no += 1

#create instance
finished = "N"
while finished != "Y":
    instance = subnet.create_instances(ImageId=ami_name,MinCount=1,MaxCount=1, KeyName=key_name,SecurityGroupIds=[ security_group.id ],UserData=user_data,InstanceType=intance_type)
    inst_resource = instance[0]
    print ("STEP "+  str(step_no) + " - Launching Instance: " + inst_resource.id)
    finished = input("Have you finished launching instances? [Y/N]: ") or "Y"

print ("=== Script Complete - Goodbye ===")
