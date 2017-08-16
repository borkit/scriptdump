__author__ = 'ahmed'



import boto3, argparse, yaml
from time import sleep
import os.path

def tag_instances(awsTags):
    reservations = ec2Client.describe_instances()
    instances  = [ i['Instances'] for i in reservations['Reservations']]
    # Iterate EC2 instances ...
    # if instance is part of Cloudformation, inherit tags from stack
    for i in instances:
        stackId = filter(lambda a:a["Key"] == 'aws:cloudformation:stack-id', i[0]['Tags'])
        if stackId:
            try:
              stack = cfClient.describe_stacks(StackName=stackId[0]['Value'])
            except:
              continue

            for t in awsTags["mandatory"] + awsTags["optional"]:
              if filter(lambda a:a["Key"] == t, i[0]['Tags']):
                  if verbose:
                    print('%s already exists on %s, skipping' % (t, i[0]['InstanceId']))
              else:
                for tag in stack['Stacks'][0]['Tags']:
                  if t in tag['Key']:
                    if verbose:
                        print('Tagging instance %s with tag %s and value %s' % (i[0]['InstanceId'], tag['Key'], tag['Value']))
                    ec2Client.create_tags(
                        Resources=[i[0]['InstanceId']],
                        Tags=[tag]
                    )
                    sleep(sleep_time)

def tag_volumes(awsTags):
    # Iterate EBS volumes ...
    volumes = ec2Client.describe_volumes()
    for v in volumes['Volumes']:
      try:
        volumeTags = v['Tags']
      except:
        volumeTags= []

      # Inherit Tags for attached volumes from EC2 instance
      if v['State'] == 'in-use':
        reservations = ec2Client.describe_instances(InstanceIds=[v['Attachments'][0]['InstanceId']])
        instances  = [ i['Instances'] for i in reservations['Reservations']]
        for t in awsTags["mandatory"] + awsTags["optional"]:
            if filter(lambda a:a["Key"] == t, volumeTags):
              if verbose:
                print('%s already exists on %s, skipping' % (t, v['VolumeId']))
            else:
                for tag in instances[0][0]['Tags']:
                  if t in tag['Key']:
                    if verbose:
                        print('Tagging volume %s with tag %s and value %s' % (v['VolumeId'], tag['Key'], tag['Value']))
                    ec2Client.create_tags(
                            Resources=[v['VolumeId']],
                            Tags=[tag]
                        )
                    sleep(sleep_time)

def tag_snapshots(awsTags):
    # Iterate EBS snapshots ...
    try:
      snapshots = ec2Client.describe_snapshots(OwnerIds=['self'])
    except:
      snapshots = []
    for s in snapshots['Snapshots']:
      try:
        snapshotTags = s['Tags']
      except KeyError:
        snapshotTags = []
      # Inherit myTags for snapshots from volumes
      try:
        volumes = ec2Client.describe_volumes(VolumeIds=[s['VolumeId']])
      except:
        # If snapshot has it's original volume delete
        continue
      for t in awsTags["mandatory"] + awsTags["optional"]:
        if filter(lambda a:a["Key"] == t, snapshotTags):
            if verbose:
                print('%s already exists on %s, skipping' % (t, s['SnapshotId']))
        else:
            try:
                if not volumes['Volumes'][0]['Tags']:
                    continue

            except KeyError:
                print('%s has no tags, skipping' % volumes['Volumes'][0]['VolumeId'])
                break
            for tag in volumes['Volumes'][0]['Tags']:
                if t in tag['Key']:
                    if verbose:
                        print('Tagging snapshot %s with tag %s and value %s' % (s['SnapshotId'], tag['Key'], tag['Value']))
                    ec2Client.create_tags(
                                Resources=[s['SnapshotId']],
                                Tags=[tag]
                            )
                    sleep(sleep_time)

def tag_elbs(awsTags):
    # Iterate ELB resources ...
    # if ELB is part of Cloudformation inherit tags from stack otherwise inherit from VPC
    elbs = elbClient.describe_load_balancers()
    for i in elbs['LoadBalancerDescriptions']:
        elbTags = elbClient.describe_tags(LoadBalancerNames=[i['LoadBalancerName']])['TagDescriptions'][0]['Tags']
        stackId = filter(lambda a:a["Key"] == "aws:cloudformation:stack-id", elbTags)
        for t in awsTags["mandatory"] + awsTags["optional"]:
            if filter(lambda a:a["Key"] == t, elbTags):
              if verbose:
                print('%s already exists on %s, skipping' % (t, i['LoadBalancerName']))
            else:
                if stackId:
                    try:
                      stack = cfClient.describe_stacks(StackName=stackId[0]['Value'])
                    except:
                      print('fail')
                      break

                    for tag in stack['Stacks'][0]['Tags']:
                      if t in tag['Key']:
                        if verbose:
                            print('Tagging ELB %s with tag %s and value %s' % (i['LoadBalancerName'], tag['Key'], tag['Value']))
                        elbClient.add_tags(
                            LoadBalancerNames=[i['LoadBalancerName']],
                            Tags=[tag]
                        )
                        sleep(sleep_time)
                else:
                    vpc = ec2Client.describe_vpcs(VpcIds=[i['VPCId']])

                    for tag in vpc['Vpcs'][0]['Tags']:
                      if filter(lambda a:a["Key"] == t, elbTags):
                          if verbose:
                            print('%s already exists on %s, skipping' % (t, i['LoadBalancerName']))
                      elif t in tag['Key']:
                        if verbose:
                            print('Tagging ELB %s with tag %s and value %s' % (i['LoadBalancerName'], tag['Key'], tag['Value']))
                        elbClient.add_tags(
                            LoadBalancerNames=[i['LoadBalancerName']],
                            Tags=[tag]
                        )
                        sleep(sleep_time)



def tag_rds(awsTags, region):
    # Iterate RDS resources ...
    # if RDS instance is part of Cloudformation inherit tags from stack otherwise inherit from VPC
    instances = rdsClient.describe_db_instances()
    # Construct the ARN to be used for looking up RDS instances
    user = iamClient.list_users()
    if user['Users']:
        accountId = user['Users'][0]['Arn'].split(':')[4]
        arnbase = 'arn:aws:rds:%s:%s:db:' % (region, accountId)
    else:
        role = iamClient.list_roles()
        accountId = role['Roles'][0]['Arn'].split(':')[4]
        arnbase = 'arn:aws:rds:%s:%s:db:' % (region, accountId)
    for i in instances['DBInstances']:
        dbarn = arnbase + i['DBInstanceIdentifier']
        rdsTags = rdsClient.list_tags_for_resource(ResourceName=dbarn)['TagList']
        stackId = filter(lambda a:a["Key"] == "aws:cloudformation:stack-id", rdsTags)
        for t in awsTags["mandatory"] + awsTags["optional"]:
            if filter(lambda a:a["Key"] == t, rdsTags):
              if verbose:
                print('%s already exists on %s, skipping' % (t, dbarn))
            else:
                if stackId:
                    try:
                      stack = cfClient.describe_stacks(StackName=stackId[0]['Value'])
                    except:
                      print('fail')
                      break

                    for tag in stack['Stacks'][0]['Tags']:
                      if t in tag['Key']:
                        if verbose:
                            print('Tagging RDS instance %s with tag %s and value %s' % (dbarn, tag['Key'], tag['Value']))
                        rdsClient.add_tags_to_resource(
                            ResourceName=dbarn,
                            Tags=[tag]
                        )
                        sleep(sleep_time)
                else:
                    vpc = ec2Client.describe_vpcs(VpcIds=[i['DBSubnetGroup']['VpcId']])

                    for tag in vpc['Vpcs'][0]['Tags']:
                      if filter(lambda a:a["Key"] == t, rdsTags):
                          if verbose:
                            print('%s already exists on %s, skipping' % (t, dbarn))
                      elif t in tag['Key']:
                        if verbose:
                            print('Tagging RDS instance %s with tag %s and value %s' % (dbarn, tag['Key'], tag['Value']))
                        rdsClient.add_tags_to_resource(
                            ResourceName=dbarn,
                            Tags=[tag]
                        )
                        sleep(sleep_time)



def main():
    global ec2Client, cfClient, elbClient, rdsClient, iamClient, sleep_time, verbose
    argparser = argparse.ArgumentParser(description='Enforces tagging of AWS Resources')
    argparser.add_argument('--profile', help='AWS Account profile to authenticate with', default=None, required=False)
    argparser.add_argument('--tags', help='Yaml file containing mandatory and optional tags to copy', required=True)
    argparser.add_argument("--verbose", help="increase output verbosity", action="store_true")
    argparser.add_argument('--region', help='AWS Region to work within, defaults to eu-central-1', default='eu-central-1', required=False)
    args = argparser.parse_args()
    profile = args.profile
    tagFile = args.tags
    verbose = args.verbose
    region = args.region
    #Run some tests to make sure we're working with a valid yaml file
    if os.path.isfile(tagFile):
        f = open(tagFile, 'r')
        awsTags = yaml.load(f)
    else:
        print('Supplied file does not exist: %s' % tagFile)
        raise Exception('Supplied file does not exist: %s' % tagFile)
    if 'mandatory' not in awsTags:
        print('This yaml file is not valid!\n It does not contain the mandatory tags!')
        raise Exception('This yaml file is not valid!\n It does not contain the mandatory tags!')
    elif 'optional' not in awsTags:
        print('This yaml file is not valid!\n It does not contain the optional tags!')
        raise Exception('This yaml file is not valid!\n It does not contain the optional tags!')
    sleep_time = 1

    if profile != None: boto3.setup_default_session(profile_name=profile)
    ec2Client = boto3.client('ec2', region_name=region)
    cfClient = boto3.client('cloudformation', region_name=region)
    elbClient = boto3.client('elb', region_name=region)
    rdsClient = boto3.client('rds', region_name=region)
    iamClient = boto3.client('iam', region_name=region)

    print('Tagging instances\n')
    tag_instances(awsTags)
    print('Tagging volumes\n')
    tag_volumes(awsTags)
    print('Tagging snapshots\n')
    tag_snapshots(awsTags)
    print('Tagging ELBs\n')
    tag_elbs(awsTags)
    print('Tagging RDS instances\n')
    tag_rds(awsTags, region)



if __name__ == '__main__':
    main()
