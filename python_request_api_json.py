# pip or pip3 install requests first
import requests

# get all stations in dublin 
r = requests.get('https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey=f5054ee21f6422a00c8247b74b556f10799ce4d4')
if r.status_code == requests.codes.ok:
    stations_json = r.json()
    
    # stations_json is a list with dictionaires
    for station in stations_json:
        print("Station name: " + station['name'] + ", Available bikes: " + str(station['available_bikes']) + "\n")
