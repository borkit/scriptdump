# coding: utf-8
#EC2 SecurityGroups delete
import boto3

# nodelete,trueを変数化
ND = 'nodelete'
TR = 'true'

def lambda_handler(event, context):
#if __name__ == '__main__': #EC2上
    ec2 = boto3.client('ec2')
    resp = ec2.describe_security_groups()
    all_list = []
    del_list = []
    #print (resp)
    for securitygroups in resp['SecurityGroups']:
      for groupid in securitygroups['GroupId']:
        all_list.append(securitygroups['GroupId'])
        #print(all_list)

        if 'Tags' in securitygroups:
          for tag in securitygroups['Tags']:
          #print(tag)

            if tag['Key'] == ND and tag['Value'] == TR:
              del_list.append(securitygroups['GroupId'])
               #print(del_list)

    diffset = set(all_list) - set(del_list)
   #print(diffset)
    targetlist = list(diffset)
    #print(targetlist)
    resp = ec2.delete_security_group(
      GroupId=targetlist
    )
