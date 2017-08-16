"""
Shows VpcId and the cidr and also check availability
cidr = (Classless Inter-Domain Routing or supernetting)
"""
import boto3

ec2 = boto3.resource('ec2')
ec2client = boto3.client('ec2')
response = ec2client.describe_vpcs()
for vpc in response["Vpcs"]:
    print("VpcId: " + vpc["VpcId"] + " uses Cidr of " + vpc["CidrBlock"] + " and is " + vpc["State"])
