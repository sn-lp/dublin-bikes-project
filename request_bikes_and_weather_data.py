import time
import requests
import json
from sql_tables import Stations, StationUpdates
from sqlalchemy import insert, create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import math
import logging
import os
from sqlalchemy.exc import SQLAlchemyError
import sys

# read config option from command line and import config file
if len(sys.argv) != 2:
    sys.exit("Invalid config file name. Please pass 'dev' or 'backup' as an argument")
elif sys.argv[1] == 'dev':
    from config import MainConfig
    config = MainConfig()
elif sys.argv[1] == 'backup':
    from config import BackupConfig
    config = BackupConfig()

logging.basicConfig(level=logging.INFO)

BIKES_API_KEY = config.JCDECAUX_API_KEY
WEATHER_API_KEY = config.OPENWEATHER_API_KEY
DB_USER = config.DB_USER
DB_PASSWORD = config.DB_PASSWORD
DB_SERVER = config.DB_SERVER
DB_PORT = config.DB_PORT
DB_NAME = config.DB_NAME


json_folder = "dublin-bikes-and-weather-data-json"

# connect to rds database
url = 'mysql+mysqlconnector://{}:{}@{}:{}/{}'.format(DB_USER, DB_PASSWORD, DB_SERVER, DB_PORT, DB_NAME)
engine = create_engine(url, echo=False)

# https://www.pythoncentral.io/understanding-python-sqlalchemy-session/
# session allows communication between this program and the database in python
Session = sessionmaker(bind=engine)
session = Session()

def call_bikes_api():
    bikes_api_response = requests.get(f'https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey={BIKES_API_KEY}')
    if bikes_api_response.status_code == 200:
        logging.info(f"Request to JCDecaux API succeeded with status code 200")
        return bikes_api_response.json()
    else:
        logging.error(f"Request to JCDecaux API failed with {bikes_api_response.status_code}: {bikes_api_response.reason}")
        return None

def call_weather_api(latitude, longitude):
    # call weather API with only current weather excluding forecast for the next hour or full day (which is by default included in the response unless we pass the 'exclude' parameter to the request)
    weather_api_response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&units=metric&appid={WEATHER_API_KEY}')
    if weather_api_response.status_code == 200:
        logging.info(f"Request to OPENWEATHER API succeeded with status code 200")
        return weather_api_response.json()
    else:
        logging.error(f"Request to OPENWEATHER API failed with {weather_api_response.status_code}: {weather_api_response.reason}")
        return None

def create_station_row_in_db(station):
    # convert the station "status" returned into a boolean to fit the data type of column isOpen
    if station['status'] == "OPEN":
        isOpen = True
    else:
        isOpen = False
    # create new instance of Stations
    new_station = Stations(stationId = station['number'], 
                                name = station['name'], 
                                address = station['address'], 
                                latitude = station['position']['lat'], 
                                longitude = station['position']['lng'], 
                                banking = station['banking'], 
                                isOpen = isOpen)
    
    try:
        session.add(new_station)
        session.commit()
        logging.info("Success: new station added to STATIONS table")
    except SQLAlchemyError as e:
        session.rollback()
        logging.error(f"Failed to add station {new_station.__dict__} to the STATIONS table with error: {e}")    

def create_station_update_row_in_db(station, weather_data, last_update_datetime):
    if not 'weather' in weather_data and not 'main' in weather_data:
        logging.error(f"OPENWEATHER API did not return expected data: {weather_data}.")
        return
    if not 'rain' in weather_data:
        rain = 0
    else:
        rain = weather_data['rain']['1h']
    if not 'snow' in weather_data:
        snow = 0
    else:
        snow = weather_data['snow']['1h']

    new_station_update = StationUpdates(stationId = station['number'],
                                            totalStands = station['bike_stands'],
                                            availableBikes = station['available_bikes'],
                                            freeStands = station['available_bike_stands'],
                                            lastUpdate = last_update_datetime,
                                            mainWeather = weather_data['weather'][0]['main'],
                                            temperature = weather_data['main']['temp'],
                                            cloudiness = weather_data['clouds']['all'],
                                            windSpeed = weather_data['wind']['speed'],
                                            rain = rain,
                                            snow = snow)
    
    try:
        session.add(new_station_update)
        session.commit()
        logging.info("Success: new station update added to STATION_UPDATES table")
    except SQLAlchemyError as e:
        session.rollback()
        logging.error(f"Failed to add update for station {new_station_update.__dict__} to the STATION_UPDATES table with error: {e}")

while True:
    try:
        # get all stations in dublin
        stations_json = call_bikes_api()

        # if status_code != 200 do
        if not stations_json:
            # sleep for 10 seconds before requesting to api again (api could be down)
            time.sleep(10)
            # go back to the try and call the api again
            continue 
        
        # create folder to store the api responses
        json_folder_exist = False
        if not os.path.exists(json_folder):
            try:
                os.mkdir(json_folder)
                json_folder_exist = True
            except Exception as e:
                logging.error(e)
        else:
            json_folder_exist = True
        
        # write bikes api json response to a file
        if json_folder_exist:
            with open(f'{json_folder}/dublin-bikes-{datetime.now()}.json', 'w') as outfile:
                logging.info(f"Writing bikes output to dublin-bikes-{datetime.now()}.json")
                json.dump(stations_json, outfile)

        for station in stations_json:
            # added this try so we can catch a 'none' value returned in any data field for each station
            # if a 'none' value is catched for a station that station is discarded and the program moves to process the next station without having to request to API again
            try:
                # check if the station already exists in the database
                station_row_exist = session.query(Stations).get(station['number'])
                if not station_row_exist:
                    # insert station in Stations
                    create_station_row_in_db(station)
                
                # last_update timestamp returned by Jcdecaux api is in miliseconds and is a float and openweather api receives timestamp in seconds and int
                # convert station['last_update'] to seconds and int
                last_update_timestamp_seconds = math.floor(station['last_update'] / 1000)

                # to store the unix timestamp in our database, mysql requires it in datetime format
                last_update_datetime = datetime.fromtimestamp(last_update_timestamp_seconds)

                # check if the station's last update is already in the database
                update_row_exist = session.query(StationUpdates).get((station['number'], last_update_datetime))
                if not update_row_exist:
                    station_latitude = station['position']['lat']
                    station_longitude = station['position']['lng']

                    # to call the api for current weather we need to use the station latitude and longitude
                    weather_data = call_weather_api(station_latitude, station_longitude)
                    # we add this sleep to make sure we stay below the limit of 60 calls/min to the weather api
                    time.sleep(1.5)

                    # if status_code != 200 do
                    if not weather_data:
                        # sleep for 10 seconds before requesting to api again (api could be down)
                        time.sleep(10)
                        # go back to the beginning of the for loop to process another station
                        continue
                    
                    # write weather api json response to a file named weather-'stationID'-'number of the station'-'datetime_requested'.json
                    # changed from using datetime.now() to last_update_datetime because they will be different and will be easier to match the data with the last_update from jcdecaux response
                    if json_folder_exist:
                        with open(f"{json_folder}/weather-stationID-{station['number']}-{last_update_datetime}.json", 'w') as outfile:
                            logging.info(f"Writing weather output to weather-stationID-{station['number']}-{last_update_datetime}.json")
                            json.dump(weather_data, outfile)

                    # insert station availability and weather updates in station_updates table
                    create_station_update_row_in_db(station, weather_data, last_update_datetime)
            except Exception as e:
                logging.error(e)


        # sleep for 5 minutes
        logging.info("I will sleep for 5 minutes.")
        time.sleep(5 * 60)
        logging.info("I will restart.")

    except Exception as e:
        logging.error(e)
