import requests
from config import Config

devConfig = Config()
API_KEY = devConfig.JCDECAUX_API_KEY

# get all stations in dublin 
r = requests.get(f'https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey={API_KEY}')
if r.status_code == requests.codes.ok:
    stations_json = r.json()
    
    station_numbers_list = []
    for station in stations_json:
        # test if there aren't duplicate station numbers for contract=Dublin 
        if station['number'] not in station_numbers_list:
            station_numbers_list.append(station['number'])
        else:
            print(station['number'] + 'is duplicate')
    # output should be 109 --> which is the number of stations returned by the API
    print(len(station_numbers_list))

