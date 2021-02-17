# pip or pip3 install requests first
import traceback
import time
import requests
import json
from config import Config

devConfig = Config()
API_KEY = devConfig.JCDECAUX_API_KEY

while True:
    try:
        # get all stations in dublin
        r = requests.get(f'https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey={API_KEY}')

        # check status code
        if r.status_code == requests.codes.ok:
            stations_json = r.json()

            # stations_json is a list with dictionaires
            for station in stations_json:
                print("Station name: " + station['name'] + ", Available bikes: " + str(station['available_bikes']) + "\n")

            #with open('stations.json', 'w') as write_file:
                #json.dump(r, write_file)

            # store data in database
            # save_to_db(r)

            # sleep for 5 minutes
            time.sleep(5 * 60)

    except:
        # if there is any problem, print the traceback
        print (traceback.format_exc())