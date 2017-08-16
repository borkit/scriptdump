"""
Preconditions
-------------
*Install boto3 python package on your box
*Set up AWS credentials
*Dynamodb field data type is either int or string. New data type will require improvements in code.
*CSV first two lines are always header and header data type.

Script Arguments
-------------
-Mandatory
    csvFile - Path to csv file location
    table - Dynamo db table name
-Optional
    writeRate - Number of records to write in table per second (default:5)
    delimiter - Delimiter for csv records (default=|)
    region - Dynamo db region name (default=us-west-2)

Sample Input
-------------
field1|field2|field3|field4|field5
string|string|string|string|int
GZ6MHDMM0IB1IR0P|A27LZ9R92G1SJ|OPEN||1

Sample Run
-------------
python csvToDynamodb.py abc.csv ABC
python csvToDynamodb.py abc.csv ABC 50 | us-east-1
"""
# Script to write csv records into dynamo db table.
# For help on prerequisites and running this script, read this blog.

from __future__ import print_function # Python 2/3 compatibility
from __future__ import division #Python 2/3 compatiblity for integer division
import argparse
import boto3
import csv
import time

# command line arguments
parser = argparse.ArgumentParser(description='Write CSV records to dynamo db table. CSV Header must map to dynamo table field names.')
parser.add_argument('csvFile', help='Path to csv file location')
parser.add_argument('table', help='Dynamo db table name')
parser.add_argument('writeRate', default=5, type=int, nargs='?', help='Number of records to write in table per second (default:5)')
parser.add_argument('delimiter', default='|', nargs='?', help='Delimiter for csv records (default=|)')
parser.add_argument('region', default='us-west-2', nargs='?', help='Dynamo db region name (default=us-west-2')
args = parser.parse_args()
print(args)

# dynamodb and table initialization
endpointUrl = "https://dynamodb." + args.region + ".amazonaws.com"
dynamodb = boto3.resource('dynamodb', region_name=args.region, endpoint_url=endpointUrl)
table = dynamodb.Table(args.table)

# write records to dynamo db
with open(args.csvFile) as csv_file:
    tokens = csv.reader(csv_file, delimiter=args.delimiter)
    # read first line in file which contains dynamo db field names
    header = tokens.next();
    # read second line in file which contains dynamo db field data types
    headerFormat = tokens.next();
    # rest of file contain new records
    for token in tokens:
       item = {}
       for i,val in enumerate(token):
         if val:
           key = header[i]
           if headerFormat[i]=='int':
             val = int(val)
           item[key] = val
       print(item)
       table.put_item(Item = item)

       time.sleep(1/args.writeRate) # to accomodate max write provisioned capacity for table
