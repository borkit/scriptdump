"""
Overview
Amazon Web Services Elastic Block Storage provides cheap, reliable storage—perfect for backups. The idea is to temporarily spin up an EC2 instance, attach your EBS volume to it and upload your files. Transferring the data via rsync allows for incremental backups which is very fast and reduces costs. Once the backup is complete, the EC2 instance is terminated. The whole process can be repeated as often as needed by attaching a new EC2 instance to the same EBS volume. I backup 12 GB from my own server weekly using this method. The backup takes about 5 minutes and my monthly bill from Amazon is around $1.

Setup Your VPC
You’ll need an AWS VPC with access to the internet. Exactly how to do this is beyond the scope of this article but you should basically follow AWS’ instructions for creating a “VPC with a Single Public Subnet”. Also make sure that
The default security group for your subnet allows inbound port 22 (SSH) and inbound port 873 (rsync)
Your subnet has “Auto-assign Public IP” enabled
You create an EBS volume in your preferred zone (location). Make sure it is large enough to store your backups.
Create Your Access Key and Key Pair

Create an Amazon EC2 key pair. You need this to connect to your EC2 instance after launching it. Download the private key and store in on your system. In my example, I have the private key stored at /home/takaitra/.ec2/takaitra-aws-key.pem Also create an access key (access key ID and secret access key) for either your root AWS account or an IAM user that has access to create instances. Make sure to save your secret key somewhere safe as you’ll only be able to download it once after creating it. I had problems using a key that had special characters (=, +, -, /, etc) so you may want to regenerate your key if it has these in it.
Install and Configure Boto 3

Assuming you have Python’s pip, installing Boto 3 is easy.

$ pip install boto3

The easiest way to set up your access credentials is via awscli.

$ pip install awscli

$ aws configure
AWS Access Key ID: [enter your access key id]
AWS Secret Access Key: [enter your secret access key]
Default region name: [enter the region name]
------------
Automation
Follow these steps in order to automate backups to Amazon EC2.
The steps may vary slightly depending on which distro you are running.
1. Save the script to a file without a file extension such as “ec2_rsync”. Cron (at least in Debian) ignores scripts with extensions.
2. Configure the script as explained above.
3. Make the script executable (chmod +x rsync_to_ec2)
4. Check that the script is working by running it manually (./ec2_rsync). This may take a long time if this is your initial backup.
5. Copy the script to /etc/cron.daily/ or /etc/cron.weekly depending on how often you want the backup to run.


------------
The Script
The below script automates the entire backup process via Boto (A Python interface to AWS). Make sure to configure the VOLUME_ID, SUBNET and BACKUP_DIRS variables with your own values. Also update SSH_OPTS to point to the private key of your EC2 key pair.
------------
"""
#!/usr/bin/env python

import os
import boto3
import time

IMAGE           = 'ami-60b6c60a' # Amazon Linux AMI 2015.09.1
KEY_NAME        = 'takaitra-key'
INSTANCE_TYPE   = 't2.micro'
VOLUME_ID       = 'vol-########'
PLACEMENT       = {'AvailabilityZone': 'us-east-1a'}
SUBNET          = 'subnet-########'
SSH_OPTS        = '-o StrictHostKeyChecking=no -i /home/takaitra/.ec2/takaitra-aws-key.pem'
BACKUP_DIRS     = ['/etc/', '/opt/', '/root/', '/home/', '/usr/local/', '/var/www/']
DEVICE          = '/dev/sdh'

print 'Starting an EC2 instance of type {0} with image {1}'.format(INSTANCE_TYPE, IMAGE)
ec2 = boto3.resource('ec2')
ec2Client = boto3.client('ec2')
ec2.create_instances(ImageId=IMAGE,InstanceType=INSTANCE_TYPE,Placement=PLACEMENT,SubnetId=SUBNET,MinCount=1,MaxCount=1,KeyName=KEY_NAME)
instances = ec2.instances.filter(
    Filters=[{'Name': 'instance-state-name', 'Values': ['pending']}])
instanceList = list(instances)
instance = instanceList[0]

print 'Waiting for instance {0} to switch to running state'.format(instance.id)
waiter = ec2Client.get_waiter('instance_running')
waiter.wait(InstanceIds=[instance.id])
instance.reload()
print 'Instance is running, public IP: {0}'.format(instance.public_ip_address)

try:
    print 'Attaching volume {0} to device {1}'.format(VOLUME_ID, DEVICE)
    volume = ec2.Volume(VOLUME_ID)
    volume.attach_to_instance(InstanceId=instance.id,Device=DEVICE)
    print 'Waiting for volume to switch to In Use state'
    waiter = ec2Client.get_waiter('volume_in_use')
    waiter.wait(VolumeIds=[VOLUME_ID])
    print 'Volume is attached'

    print 'Waiting for the instance to finish booting'
    time.sleep(60)
    print 'Mounting the volume'
    os.system("ssh -t {0} ec2-user@{1} \"sudo mkdir /mnt/data-store && sudo mount {2} /mnt/data-store && echo 'Defaults !requiretty' | sudo tee /etc/sudoers.d/rsync > /dev/null\"".format(SSH_OPTS, instance.public_ip_address, DEVICE))

    print 'Beginning rsync'
    for backup_dir in BACKUP_DIRS:
            os.system("sudo rsync -e \"ssh {0}\" -avz --delete --rsync-path=\"sudo rsync\" {2} ec2-user@{1}:/mnt/data-store{2}".format(SSH_OPTS, instance.public_ip_address, backup_dir))
    print 'Rsync complete'

    print 'Unmounting and detaching volume'
    os.system("ssh -t {0} ec2-user@{1} \"sudo umount /mnt/data-store\"".format(SSH_OPTS, instance.public_ip_address))
    volume.detach_from_instance(InstanceId=instance.id)
    print 'Waiting for volume to switch to Available state'
    waiter = ec2Client.get_waiter('volume_available')
    waiter.wait(VolumeIds=[VOLUME_ID])
    print 'Volume is detached'
finally:
    print 'Terminating instance'
    instance.terminate()
