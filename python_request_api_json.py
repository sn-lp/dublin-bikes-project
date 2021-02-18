# pip or pip3 install requests first
import requests
from config import Config

devConfig = Config()
API_KEY = devConfig.JCDECAUX_API_KEY

# get all stations in dublin 
r = requests.get(f'https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey={API_KEY}')
if r.status_code == requests.codes.ok:
    stations_json = r.json()
    
    # stations_json is a list with dictionaires
    for station in stations_json:
        print("Station name: " + station['name'] + station["position"] + ", Available bikes: " + str(station['available_bikes']) + "\n")
