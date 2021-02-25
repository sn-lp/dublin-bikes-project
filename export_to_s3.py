import boto3
from config import Config
import os

s3 = boto3.client('s3')

devConfig = Config()
S3_BUCKET = devConfig.S3_BUCKET

# Take all the files in dublin-bikes-json folder and push them to S3
for filename in os.listdir('dublin-bikes-json'):
    s3.upload_file(
        Filename=f'dublin-bikes-json/{filename}',
        Bucket=S3_BUCKET,
        Key=filename
    )
