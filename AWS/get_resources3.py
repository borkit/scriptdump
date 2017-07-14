"""
Another variation of get_resources,
gets Subnets, VPCs and ec2 security Groups
requires BOTO3 installed.
"""

import json
import boto3

#ec2client = boto3.client('ec2')
#response = ec2client.describe_instances()
#for reservation in response["Reservations"]:
#    for instance in reservation["Instances"]:
#        # This sample print will output entire Dictionary object
#        print(instance)
#        # This will print will output the value of the Dictionary key 'InstanceId'
#        print(instance["InstanceId"])

ec2 = boto3.resource('ec2', region_name='us-east-1')
client = boto3.client('ec2')

filters = [{'Name':'tag:Name', 'Values':['*']}]
#vpcs = list(ec2.vpcs.filter(Filters=filters))
#
#for vpc in vpcs:
#    response = client.describe_vpcs(
#        VpcIds=[
#            vpc.id,
#        ]
#    )
#    print(json.dumps(response, sort_keys=True, indent=4))

#for i in  ec2.instances.all(): print(i)
print('Sunets:')
for s in  ec2.subnets.all(): print(s)
print('VPCs:')
for v in ec2.vpcs.all(): print(v)
print('Security Groups:')
for sec in ec2.security_groups.all(): print (sec)
