#!/usr/bin/python
import boto3
import logging
import argparse
from pprint import pformat,pprint

parser = argparse.ArgumentParser(description='Cross reference existing ec2 reservations to current instances.')
parser.add_argument('--log', default="WARN", help='Change log level (default: WARN)')
parser.add_argument('--region', default='us-east-1', help='AWS Region to connect to')

args = parser.parse_args()

logging.basicConfig(level=getattr(logging, args.log))
logger = logging.getLogger('ec2-check')

# Dump some environment details
logger.debug("boto version = %s", boto3.__version__)

ec2_client = boto3.client('ec2',
                          region_name=args.region)

ec2_instances = ec2_client.describe_instances()
running_ec2_instances = {}
for reservation in ec2_instances['Reservations']:
    for instance in reservation['Instances']:
        if instance['State']['Name'] != "running":
            logger.debug("Disqualifying instance %s: not running\n" % ( instance['InstanceId'] ) )
        elif "InstanceLifecycle" in instance:
            if instance['InstanceLifecycle'] == "spot":
                logger.debug("Disqualifying instance %s: spot\n" % ( instance['InstanceId'] ) )
        else:
            az = instance['Placement']['AvailabilityZone']
            instance_type = instance['InstanceType']
            logger.debug("Running instance: %s"% (instance))
            if "VpcId" in instance:
                location = 'vpc'
            else:
                location = 'ec2'
            if "Platform" in instance:
                platform = instance['Platform']
            else:
                platform = 'linux'
            running_ec2_instances[ (instance_type, az, platform, location ) ] = running_ec2_instances.get( (instance_type, az, platform, location ) , 0 ) + 1

logger.debug("FOO -- Running instances: %s"% pformat(running_ec2_instances))
ec2_reservations = ec2_client.describe_reserved_instances()

ec2_reserved_instances = {}
ec2_reserved_instances_ids = {}

for ri in ec2_reservations['ReservedInstances']:
    if ri['State'] != "active":
        logger.debug("Excluding reserved instances %s: no longer active\n" % (ri['ReservedInstancesId']))
    else:
        if ri['Scope'] != "Region":
            az = ri['AvailabilityZone']
        else:
            az = 'Region'
        instance_type = ri['InstanceType']
        logger.debug("Reserved instance: %s" % (ri))
        description = ri['ProductDescription']
        if "Windows" in description:
            platform = 'windows'
        else:
            platform = 'linux'
        if "VPC" in description:
            location = 'vpc'
        else:
            location = 'ec2'
        instance_signature = (instance_type, az, platform, location)
        ec2_reserved_instances[instance_signature] = ec2_reserved_instances.get(instance_signature,
                                                                                0) + ri['InstanceCount']
        if instance_signature not in ec2_reserved_instances_ids:
            # print "Resetting instance_signature: (%s)" % (instance_signature)
            ec2_reserved_instances_ids[instance_signature] = []
        logger.debug("inserting reserved_instance_id (%s) into list (%s)" % (
        instance_signature, ec2_reserved_instances_ids[instance_signature]))
        ec2_reserved_instances_ids[instance_signature].append(ri['ReservedInstancesId'])

logger.debug("Reserved instances: %s" % pformat(ec2_reserved_instances))


for running_instance in running_ec2_instances:
    for _ in range(running_ec2_instances[running_instance]):
        if running_instance in ec2_reserved_instances:
            if ec2_reserved_instances[running_instance] >= 2:
                ec2_reserved_instances[running_instance] -= 1
            else:
                ec2_reserved_instances.pop(running_instance)
                logger.debug("Instance is not reserved")
        else:
            regional_running_reservation = list(running_instance)
            regional_running_reservation[1] = 'Region'
            regional_running_reservation_tuple = tuple(regional_running_reservation)
            if regional_running_reservation_tuple in ec2_reserved_instances:
                if ec2_reserved_instances[regional_running_reservation_tuple] >= 2:
                    ec2_reserved_instances[regional_running_reservation_tuple] -= 1
                else:
                    ec2_reserved_instances.pop(regional_running_reservation_tuple)
                    logger.debug("Instance is not reserved")

print ("Unused reserved instances: %s" % pformat(ec2_reserved_instances))
