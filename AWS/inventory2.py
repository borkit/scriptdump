#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

import argparse, sys, boto3, pprint

def count(my_list, my_key):
    if my_key not in my_list:
        return '0'
    else:
        return str(len(my_list[my_key]))

parser = argparse.ArgumentParser(description='Show all EC2 and RDS instances in your AWS account, grouped by VPC.')
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
        rdsclient = session.client('rds', region)

        instances = {}
        dbs = {}

        ec2_instances = ec2client.describe_instances(Filters=[ { 'Name': 'instance-state-name', 'Values': [ 'running' ] } ])
        for reservation in ec2_instances['Reservations']:
            for instance in reservation['Instances']:
                instance_name = instance['InstanceId']
                if instance.get('Tags'):
                    for tag in instance['Tags']:
                        if tag['Key'] == 'Name':
                            instance_name = instance['InstanceId'] + ' (' + tag['Value'] + ')'
                if instance['VpcId'] in instances:
                    instances[instance['VpcId']].append(instance_name)
                else:
                    instances[instance['VpcId']] = [ instance_name ]

        db_instances = rdsclient.describe_db_instances()
        for db_instance in db_instances['DBInstances']:
            if 'DBSubnetGroup' in db_instance:
                db_vpc = db_instance['DBSubnetGroup']['VpcId']
                if db_vpc in dbs:
                    dbs[db_vpc].append(db_instance['DBInstanceIdentifier'])
                else:
                    dbs[db_vpc] = [ db_instance['DBInstanceIdentifier'] ]

        vpcs = ec2client.describe_vpcs()
        for vpc in vpcs['Vpcs']:
            if vpc['IsDefault'] == False:
                vpc_id = vpc['VpcId']
                if vpc.get('Tags'):
                    for tag in vpc['Tags']:
                        if tag['Key'] == "Name":
                            vpc_name = tag['Value']
                print('\033[1;32;40m' + vpc_id + ' | ' + vpc_name + ' | ' + vpc['CidrBlock'] + ' (' + count(instances, vpc_id)  + ' ec2 instances, ' + count(dbs, vpc_id) + ' rds instances)\033[0;37;40m')
                if vpc_id in instances:
                    print('\033[1;33;40m    ec2 instances: \033[0;37;40m' + ','.join(instances[vpc_id]))
                if vpc_id in dbs:
                    print('\033[1;35;40m    rds instances: \033[0;37;40m' + ','.join(dbs[vpc_id]))
