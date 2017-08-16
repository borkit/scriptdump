# coding: utf-8
#EC2に紐付いていないEIPを開放
import boto3

def lambda_handler(event, context):
#if __name__ == '__main__': #EC2
    client = boto3.client('ec2', "ap-northeast-1")
    resp = client.describe_addresses()
    #print(resp)

    for addresses in resp['Addresses']:
        #print(addresses['AllocationId'])
        if not 'InstanceId' in addresses:
            #print(addresses['AllocationId'])

            client.release_address(
                AllocationId=addresses['AllocationId']
            )
