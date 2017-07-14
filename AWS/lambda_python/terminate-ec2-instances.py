#Keyがnodelete、Valueがtrue以外は削除
# coding: utf-8
# EC2 terminate
import boto3

#nodelete,trueを変数化
ND = 'nodelete'
TR = 'true'

def lambda_handler(event, context):
#if __name__ == '__main__': #EC2上で
    client = boto3.client('ec2')
    resp = client.describe_instances()
    all_list = []
    del_list = []

    for reservation in resp['Reservations']:
      for instance in reservation['Instances']:
        all_list.append(instance['InstanceId'])
        #print(all_list)

        if 'Tags' in instance:

          #nodelete以外は削除
          for tag in instance['Tags']:
            if tag['Key'] == ND and tag['Value'] == TR:
              del_list.append(instance['InstanceId'])
              #print(del_list)

    diffset = set(all_list) - set(del_list)
    #print(diffset)
    targetlist = list(diffset)
    #print(targetlist)
    ec2.terminate_instances(
      InstanceIds=targetlist
    )
