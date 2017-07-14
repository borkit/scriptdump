# coding: utf-8
#ELB delete
import boto3

# nodelete,trueを変数化
ND = 'nodelete'
TR = 'true'

def lambda_handler(event, context):
#if __name__ == '__main__': #EC2の場合
  client = boto3.client('elb')

#loadbalancersの情報を変数化
  resp = client.describe_load_balancers()
  all_list1 = []
  del_list1 = []

#loadbalancerNameでtagを出力
  #print resp
  for elb in resp['LoadBalancerDescriptions']:
    all_list1.append(elb['LoadBalancerName'])
    #print(all_list)
    resp2 = client.describe_tags(
      LoadBalancerNames=[elb['LoadBalancerName']]
    )
     #print(resp2)
    for tag in resp2['TagDescriptions']:
          #tagがnodelete以外を出力
          for k in tag['Tags']:
            #print k
            if k['Key'] == ND and k['Value'] == TR:
              del_list1.append(elb['LoadBalancerName'])
              #print(del_list)
    diffset1 = set(all_list1) - set(del_list1)
    #print(diffset)
    targetlist1 = list(diffset1)
    #print(targetlist1)
    response = client.delete_load_balancer(
      LoadBalancerName=targetlist1
    )

#ALB delete
def lambda_handler(event, context):
#if __name__ == '__main__':
  client = boto3.client('elbv2')

 #loadbalancersの情報を変数化
  resp = client.describe_load_balancers()
  all_list2 = []
  del_list2 = []

  #loadbalancerNameでtagを出力
    #print resp
  for alb in resp['LoadBalancers']:
    all_list2.append(alb['LoadBalancerArn'])
    #print(all_list2)
    resp2 = client.describe_tags(
      ResourceArns=[alb['LoadBalancerArn']]
    )
     #print(resp2)
    for tag in resp2['TagDescriptions']:
          #tagがnodelete以外を出力
          for a in tag['Tags']:
            #print a
            if a['Key'] == ND and a['Value'] == TR:
               del_list2.append(alb['LoadBalancerArn'])
              #print(del_list)
  diffset2 = set(all_list2) - set(del_list2)
  #print(diffset2)
  targetlist2 = list(diffset2)
  #print(targetlist2)
  response = client.delete_load_balancer(
    LoadBalancerArn=targetlist2
  )
