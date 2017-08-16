# coding: utf-8
# RDS delete
import boto3

# nodelete,trueを変数化
ND = 'nodelete'
TR = 'true'

def lambda_handler(event, context):
#if __name__ == '__main__':
    client = boto3.client('rds', "ap-northeast-1")
    resp = client.describe_db_snapshots()
    #print resp
    all_list = []
    del_list = []

    for rds in resp['DBSnapshots']:
        all_list.append(rds['DBSnapshotIdentifier'])
        #print(all_list)

        resp2 = client.list_tags_for_resource(
            ResourceName="arn:aws:rds:ap-northeast-1:xxxxxxxxxxxx:snapshot:" + rds['DBSnapshotIdentifier']
        )
        #print resp2

        for tag in resp2['TagList']:
            #print tag
            if tag['Key'] == ND and tag['Value'] == TR:
                del_list.append(rds['DBSnapshotIdentifier'])
                #print(del_list)

    diffset = set(all_list) - set(del_list)
    #print(diffset)
    targetlist = list(diffset)
    #print(targetlist)

    for target in targetlist:
        #print target
        response = client.delete_db_snapshot(
        DBSnapshotIdentifier=target,
        SkipFinalSnapshot=True
        )
