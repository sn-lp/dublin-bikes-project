# pip or pip3 install requests first
import traceback
import time
import requests
import json
from config import Config
import boto3
import json
import datetime

s3 = boto3.client('s3')

devConfig = Config()
API_KEY = devConfig.JCDECAUX_API_KEY

while True:
    try:
        # get all stations in dublin
        r = requests.get(f'https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey={API_KEY}')

        # check status code
        if r.status_code == requests.codes.ok:
            stations_json = r.json()

        # store json on S3
        s3.put_object(
            Body=json.dumps(r),
            Bucket='dublin-bikes-data',
            Key=f'dublin-bikes-{datetime.datetime.now()}.json'
        )

        # sleep for 5 minutes
        time.sleep(5 * 60)

    # boto3 exceptions
    except Exceptions as e:
        print ("Exception ", e)

    except:
        # if there is any problem, print the traceback
        print (traceback.format_exc())
