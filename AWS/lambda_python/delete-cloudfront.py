# coding: utf-8
# RDS delete
import boto3

# nodelete,trueを変数化
ND = 'nodelete'
TR = 'true'

def lambda_handler(event, context):
#if __name__ == '__main__':
    client = boto3.client('cloudfront', "ap-northeast-1")
    resp = client.list_distributions()
    #print resp
    all_list = []
    del_list = []

    for cf in resp['DistributionList']['Items']:
        #print cf['Id']
        all_list.append(cf['Id'])
        #print all_list

        resp2 = client.list_tags_for_resource(
            Resource = "arn:aws:cloudfront::xxxxxxxxxxxxxxxxx:distribution/" + cf['Id']
         )
        #print resp2
        for tag in resp2['Tags']['Items']:
            #print tag

            if tag['Key'] == ND and tag['Value'] == TR:
                del_list.append(cf['Id'])
                #print(del_list)

    diffset = set(all_list) - set(del_list)
    #print(diffset)
    targetlist = list(diffset)
    #print(targetlist)

    for target in targetlist:
        #print target
        response = client.delete_distribution(
            Id=target
        )
