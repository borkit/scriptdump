
"""
This script gets VPCs and ec2 Subnets
"""
import boto3
ec2 = boto3.resource('ec2', region_name='us-east-1')
vpc = ec2.Vpc('*')
client = boto3.client('ec2')

print('VPCs:')
for v in ec2.vpcs.all(): print(v)

print('-------------------------------------')

print('Subnets:')
for s in  ec2.subnets.all(): print(s)
#print('Security Groups:')
#for sec in ec2.security_groups.all(): print (sec)


#print(vpc.cidr_block)
#print(vpc.state)

vpclist = vpc.instances.all()
for instance in vpclist:
    print(instance)
