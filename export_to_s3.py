import boto3
import os
import sys

# read config option from command line and import config file
import importlib.util
spec = importlib.util.spec_from_file_location("config",'config_{}.py'.format(sys.argv[1]))
module = importlib.util.module_from_spec(spec)
sys.modules["config"] = module
spec.loader.exec_module(module)
from config import Config

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
