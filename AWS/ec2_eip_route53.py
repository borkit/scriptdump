import boto3
dryRun = False; # useful variable to put the script into dry run mode where the function allows it

ec2Client = boto3.client('ec2')
ec2Resource = boto3.resource('ec2')

# Create the instance
instanceDict = ec2Resource.create_instances(
    DryRun = dryRun,
    ImageId = "YOUR_AMI_ID",
    KeyName = "YOUR_KEY_PAIR_NAME",
    InstanceType = "t1.micro",
    SecurityGroupIds = ["YOUR_SECURITY_GROUP_ID"],
    MinCount = 1,
    MaxCount = 1
)
# Wait for it to launch before assigning the elastic IP address
instanceDict[0].wait_until_running();

# Allocate an elastic IP
eip = ec2Client.allocate_address(DryRun=dryRun, Domain='vpc')
# Associate the elastic IP address with the instance launched above
ec2Client.associate_address(
     DryRun = dryRun,
     InstanceId = instanceDict[0].id,
     AllocationId = eip["AllocationId"])

route53Client = boto3.client('route53')
#Now add the route 53 record set to the hosted zone for the domain
route53Client.change_resource_record_sets(
    HostedZoneId = 'YOUR_ZONE_ID',
    ChangeBatch= {
    'Comment': 'Add new instance to Route53',
    'Changes': [
    {
        'Action': 'CREATE',
        'ResourceRecordSet': {
            'Name': 'YOUR_DNS_ENTRY',
            'Type': 'A',
            'TTL': 60,
            'ResourceRecords': [
            {
                'Value': eip["PublicIp"]
            },
            ],
        }
    },
    ]
})
