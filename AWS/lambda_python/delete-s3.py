# coding: utf-8
# RDS delete
import boto3

# nodelete,trueを変数化
ND = 'nodelete'
TR = 'true'

def lambda_handler(event, context):
#if __name__ == '__main__':
    client = boto3.client('s3', "ap-northeast-1")
    resp = client.list_buckets()
    #print resp
    all_list = []
    del_list = []

    for s3 in resp['Buckets']:
        #print s3
        all_list.append(s3['Name'])
        #print(all_list)

        try:
            resp2 = client.get_bucket_tagging(
                Bucket=s3['Name']
            )
        except:
            None
        #print s3['Name']

        for tag in resp2['TagSet']:
            #print tag
                if tag['Key'] == ND and tag['Value'] == TR:
                     del_list.append(s3['Name'])
                     #print(del_list)

    diffset = set(all_list) - set(del_list)
    #print(diffset)
    targetlist = list(diffset)
    #print(targetlist)


    for target in targetlist:
        #print target
#        #print type(target)
        response = client.delete_bucket(
        Bucket=target
        )
