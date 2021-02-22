# pip or pip3 install requests first
import traceback
import time
import requests
import json
from config import Config

devConfig = Config()
API_KEY = devConfig.JCDECAUX_API_KEY

# initialise list
data_list = []

while True:
    try:
        # get all stations in dublin and save as json file
        r = requests.get(f'https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey={API_KEY}').json()

        # append request to json file
        data_list.append(r)

        # open destination file and write data object to outfile
        with open("data.json", "w") as outfile:
            json.dump(data_list, outfile)

        # TODO store data.json on S3

        # sleep for 5 minutes
        time.sleep(5 * 60)

    except:
        # if there is any problem, print the traceback
        print(traceback.format_exc())


