import time
import requests
import json
import datetime
from config import Config
import logging

logging.basicConfig(level=logging.INFO)

devConfig = Config()
API_KEY = devConfig.JCDECAUX_API_KEY

while True:
    try:
        # make a request to JCDecaux API
        response = requests.get(f'https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey={API_KEY}')

        if response.status_code == 200:
            logging.info(f"Request to JCDecaux API succeeded with status code 200")

            with open(f'dublin-bikes-json/dublin-bikes-{datetime.datetime.now()}.json', 'w') as outfile:
                logging.info(f"Writing output to dublin-bikes-{datetime.datetime.now()}.json")
                json.dump(response.json(), outfile)

        else:
            logging.error(f"Request to JCDecaux API failed with {response.status_code}: {response.reason}")

        # sleep for 5 minutes
        time.sleep(5 * 60)

    except Exception as e:
        logging.error(e)
