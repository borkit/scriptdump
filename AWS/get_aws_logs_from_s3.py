#! /usr/bin/env python
"""Download and delete log files for AWS S3 / CloudFront

Usage: python get-aws-logs.py [options]

Options:
  -b ..., --bucket=...    AWS Bucket
  -p ..., --prefix=...    AWS Key Prefix
  -a ..., --access=...    AWS Access Key ID
  -s ..., --secret=...    AWS Secret Access Key
  -l ..., --local=...     Local Download Path
  -h, --help              Show this help
  -d                      Show debugging information while parsing

Examples:
  get-aws-logs.py -b eqxlogs
  get-aws-logs.py --bucket=eqxlogs
  get-aws-logs.py -p logs/cdn.example.com/
  get-aws-logs.py --prefix=logs/cdn.example.com/

This program requires the boto module for Python to be installed.
"""

__author__ = "Johan Steen (https://code.bitbebop.com/)"
__version__ = "0.5.0"
__date__ = "28 Nov 2010"

import boto
import getopt
import sys, os

_debug = 0

class get_logs:
    """Download log files from the specified bucket and path and then delete them from the bucket.
    Uses: http://boto.s3.amazonaws.com/index.html
    """
    # Set default values
    AWS_BUCKET_NAME = '{bucket}'
    AWS_KEY_PREFIX = '{prefix}'
    AWS_ACCESS_KEY_ID = '{access key}'
    AWS_SECRET_ACCESS_KEY = '{secret key}'
    LOCAL_PATH = '{local path}'
    # Don't change below here
    s3_conn = None
    bucket_list = None

    def __init__(self):
        s3_conn = None
        bucket_list = None

    def start(self):
        """Connect, get file list, copy and delete the logs"""
        self.s3Connect()
        self.getList()
        self.copyFiles()

    def s3Connect(self):
        """Creates a S3 Connection Object"""
        self.s3_conn = boto.connect_s3(self.AWS_ACCESS_KEY_ID, self.AWS_SECRET_ACCESS_KEY)

    def getList(self):
        """Connects to the bucket and then gets a list of all keys available with the chosen prefix"""
        bucket = self.s3_conn.get_bucket(self.AWS_BUCKET_NAME)
        self.bucket_list = bucket.list(self.AWS_KEY_PREFIX)

    def copyFiles(self):
        """Creates a local folder if not already exists and then download all keys and deletes them from the bucket"""
        # Using makedirs as it's recursive
        if not os.path.exists(self.LOCAL_PATH):
            os.makedirs(self.LOCAL_PATH)
        for key_list in self.bucket_list:
            key = str(key_list.key)
            # Get the log filename (L[-1] can be used to access the last item in a list).
            filename = key.split('/')[-1]
            # check if file exists locally, if not: download it
            if not os.path.exists(self.LOCAL_PATH+filename):
                key_list.get_contents_to_filename(self.LOCAL_PATH+filename)
                if _debug:
                    print "Downloaded from bucket: "+filename
            # check so file is downloaded, if so: delete from bucket
            if os.path.exists(self.LOCAL_PATH+filename):
                key_list.delete()
                if _debug:
                    print "Deleted from bucket:    "+filename

def usage():
    print __doc__

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hb:p:l:a:s:d", ["help", "bucket=", "prefix=", "local=", "access=", "secret="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    logs = get_logs()
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt == '-d':
            global _debug
            _debug = 1
        elif opt in ("-b", "--bucket"):
            logs.AWS_BUCKET_NAME = arg
        elif opt in ("-p", "--prefix"):
            logs.AWS_KEY_PREFIX = arg
        elif opt in ("-a", "--access"):
            logs.AWS_ACCESS_KEY_ID = arg
        elif opt in ("-s", "--secret"):
            logs.AWS_SECRET_ACCESS_KEY = arg
        elif opt in ("-l", "--local"):
            logs.LOCAL_PATH = arg
    logs.start()

if __name__ == "__main__":
    main(sys.argv[1:])
