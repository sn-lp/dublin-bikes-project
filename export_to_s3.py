import boto3
import os
import sys

# read config option from command line and import config file
if sys.argv[1] == 'dev':
    from config_dev import Config
elif sys.argv[1] == 'backup':
    from config_backup import Config
else:
    exit("Invalid config file name. Please pass 'dev' or 'backup' as an argument")

s3 = boto3.client('s3')

devConfig = Config()
S3_BUCKET = devConfig.S3_BUCKET

# Take all the files in dublin-bikes-json folder and push them to S3
for filename in os.listdir('dublin-bikes-and-weather-data-json'):
    s3.upload_file(
        Filename=f'dublin-bikes-and-weather-data-json/{filename}',
        Bucket=S3_BUCKET,
        Key=filename
    )
