#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

import argparse, sys, boto3, pprint

parser = argparse.ArgumentParser(description='Find VPCs that contain no EC2 instances')
parser.add_argument('--aws-key', dest='aws_key', help='AWS Key')
parser.add_argument('--aws-secret-key', dest='aws_secret_key', help='AWS Secret Key')
parser.add_argument('--region', dest='region', help='Limit to a single region')
args = parser.parse_args()

if args.aws_key and args.aws_secret_key:
    session = boto3.Session(aws_access_key_id=args.aws_key, aws_secret_access_key=args.aws_secret_key)
else:
    session = boto3.Session()

regions = session.get_available_regions('ec2')

for region in regions:
    print("Region: " + region)
    if (not args.region) or (args.region == region):
        ec2client = session.client('ec2', region)

        instances = {}

        ec2_instances = ec2client.describe_instances(Filters=[ { 'Name': 'instance-state-name', 'Values': [ 'running' ] } ])
        for reservation in ec2_instances['Reservations']:
            for instance in reservation['Instances']:
                if instance['VpcId'] in instances:
                    instances[instance['VpcId']].append(instance['InstanceId'])
                else:
                    instances[instance['VpcId']] = [ instance['InstanceId'] ]
        vpcs = ec2client.describe_vpcs()

        for vpc in vpcs['Vpcs']:
            if vpc['IsDefault'] == False:
                contents = ', '.join(instances[vpc['VpcId']]) if vpc['VpcId'] in instances else 'empty'
                print(vpc['VpcId'] + ' ' + vpc['CidrBlock'] + ' ' + contents)
