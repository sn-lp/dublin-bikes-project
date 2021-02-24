import time
import requests
import boto3
import json
import datetime
from config import Config


s3 = boto3.client('s3')

devConfig = Config()
API_KEY = devConfig.JCDECAUX_API_KEY
S3_BUCKET = devConfig.S3_BUCKET

while True:
    try:
        # get all stations in dublin
        r = requests.get(f'https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey={API_KEY}').json()

        # store json on S3
        s3.put_object(
            Body=json.dumps(r),
            Bucket=S3_BUCKET,
            Key=f'dublin-bikes-{datetime.datetime.now()}.json'
        )

        # sleep for 5 minutes
        time.sleep(5 * 60)

    # boto3 exceptions
    except Exception as e:
        print ("Exception ", e)
