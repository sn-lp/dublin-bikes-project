from flask import g, render_template, jsonify, request, abort
from webapp import app
from sql_tables import Stations, StationUpdates
from sqlalchemy import insert, create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import sys
from functools import lru_cache
import requests
import logging
from datetime import datetime
import calendar
import math
import pickle
from sklearn.feature_extraction import DictVectorizer

DB_USER = app.config["DB_USER"]
DB_PASSWORD = app.config["DB_PASSWORD"]
DB_SERVER = app.config["DB_SERVER"]
DB_PORT = app.config["DB_PORT"]
DB_NAME = app.config["DB_NAME"]
OPENWEATHER_API_KEY = app.config["OPENWEATHER_API_KEY"]

def get_station_availability_averages(station_property, station):
    # in mysql days of the week are represented by nnumbers from 0 to 6 (0 = Monday)
    weekdays = [0, 1, 2, 3, 4, 5, 6]
    availability_history = {}
    for day in weekdays:
        rows = g._database.execute(f"select ROUND(avg({station_property}), 0), hour(lastUpdate) from station_updates where stationId = {station} and weekday(lastUpdate) = {day} group by hour(lastUpdate)  order by hour(lastUpdate) asc;")
        availability_history[day] = []
        for row in rows:
            availability_history[day].append({f"{station_property}":int(row[0]), "hour": row[1]})
    return availability_history

def get_day_of_the_week(user_timestamp_input):
    dt_obj = datetime.fromtimestamp(user_timestamp_input)
    dt_weekday_number = dt_obj.weekday()
    dt_weekday_name = calendar.day_name[dt_weekday_number]
    return dt_weekday_name

def get_hour(user_timestamp_input):
    dt_obj = datetime.fromtimestamp(user_timestamp_input)
    dt_hour = dt_obj.hour
    return dt_hour

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/predictions")
def predictions():
    return render_template('prediction.html')

def connect_to_database():
    url = 'mysql+mysqlconnector://{}:{}@{}:{}/{}'.format(DB_USER, DB_PASSWORD, DB_SERVER, DB_PORT, DB_NAME)
    engine = create_engine(url, echo=False)
    return engine

# we need this decorator to open the connection to the database before each request
@app.before_request
def open_db_connection():
    # stores the connection to the database in globals as a variable called "_database"
    g._database = connect_to_database().connect()

# this is executed at the end of a request
@app.teardown_appcontext
def close_db_connection(exception):
    # we don't want to close the engine as we had before, just the connection
    # check if _database exists in globals before closing
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/stations")
@lru_cache
def get_stations():
    stations = pd.read_sql("SELECT * FROM stations", g._database)
    availability = pd.read_sql("SELECT * FROM station_updates", g._database)
    # Get the latest availability update for each station
    latest_availability = availability.sort_values("lastUpdate").groupby("stationId").tail(1)
    # Combine with static stations data
    stations_with_availability = stations.merge(latest_availability, on="stationId", how='inner')
    return stations_with_availability.to_json(orient="records")

@app.route("/availability_history")
def get_station_availability_history():
    # we need to have a query parameter to know which station Id we are dealing with
    station = request.args.get('stationId')
    # if there is no query parameter
    if not station:
        abort(400)
    return get_station_availability_averages("availableBikes", station)


@app.route("/weatherWidget.js")
def weatherWidget_js():
    return render_template('weatherWidget.js',
                           openweather_api=app.config['OPENWEATHER_API_KEY'])

@app.route("/available_spaces_history")
def get_station_available_spaces_history():
    station = request.args.get('stationId')
    if not station:
        abort(400)
    return get_station_availability_averages("freeStands", station)

@app.route("/weather_forecast_and_availability_prediction")
def get_weather_forecast_and_prediction_for_station():
    station_number = request.args.get('stationNumber')
    station_latitude = request.args.get('stationLat')
    station_longitude = request.args.get('stationLong')
    time_requested_unix_timestamp = request.args.get('timeRequested')
    if not station_latitude or not station_longitude or not time_requested_unix_timestamp or not station_number:
        abort(400)

    # convert timestamp and station_number to int type again (when it is passed as a query parameter it is a string)
    time_requested_unix_timestamp = int(time_requested_unix_timestamp)
    station_number = int(station_number)
    # get day of the week as a string to feed the prediction model 
    day_of_the_week_string = get_day_of_the_week(time_requested_unix_timestamp)
    # get hour as an int to get the sine and cosine
    hour_of_the_day_int = get_hour(time_requested_unix_timestamp)
    # get sine and cosine of the full hour to feed the prediction model
    hour_sin = math.sin(2 * math.pi * hour_of_the_day_int/23.0)
    hour_cos = math.cos(2 * math.pi * hour_of_the_day_int/23.0)

    # request weather forecast from openweather api
    weather_forecast_api_response = requests.get(f'https://api.openweathermap.org/data/2.5/onecall?lat={station_latitude}&lon={station_longitude}&exclude=current,minutely,daily&units=metric&appid={OPENWEATHER_API_KEY}')
    if weather_forecast_api_response.status_code == 200:
        logging.info("Request to Openweather Forecast API succeeded with status code 200")
        hourly_weather_forecast = weather_forecast_api_response.json()
        if not 'hourly' in hourly_weather_forecast:
            logging.error(f"OPENWEATHER Forecast API did not return expected data: {hourly_weather_forecast}.")
            abort(400)
        else:
            for i in range(len(hourly_weather_forecast["hourly"])):
                if hourly_weather_forecast["hourly"][i]["dt"] == time_requested_unix_timestamp:
                    # get the weather variables from the api that correspond to the ones we are also storing in our (historical data) database
                    main_weather = hourly_weather_forecast["hourly"][i]["weather"][0]["main"]
                    temperature = hourly_weather_forecast["hourly"][i]["temp"]
                    cloudiness = hourly_weather_forecast["hourly"][i]["clouds"]
                    wind_speed = hourly_weather_forecast["hourly"][i]["wind_speed"]
                    # get weather icon string from api that we can use to show the weather forecast to the user
                    weather_icon = hourly_weather_forecast["hourly"][i]["weather"][0]["icon"]
                    if not 'rain' in hourly_weather_forecast["hourly"][i]:
                        rain = 0
                    else:
                        rain = hourly_weather_forecast["hourly"][i]["rain"]["1h"]
                    if not 'snow' in hourly_weather_forecast["hourly"][i]:
                        snow = 0
                    else:
                        snow = hourly_weather_forecast["hourly"][i]["snow"]["1h"]
                    
                    # load pickle file for corresponding station which has the ML model learned for the station
                    station_model_unpickled = pickle.load( open(f"./station_models/randomForest_stationID_{station_number}", "rb"))
                    # station_model_obj is a tuple with (stationId, model)
                    station_model = station_model_unpickled[1]
                    
                    # shape user and weather data to pass as argument to the predict method
                    # build a dictionary with the features used to train the model as keys and assign the values from user input and weather forecast above
                    features = ['temperature', 'cloudiness', 'windSpeed', 'rain', 'snow', 'hour_sin', 'hour_cos',
                                    'weekday_Monday', 'weekday_Saturday', 'weekday_Sunday', 'weekday_Thursday', 'weekday_Tuesday',
                                    'weekday_Wednesday', 'mainWeather_Clouds', 'mainWeather_Drizzle', 'mainWeather_Fog',
                                    'mainWeather_Mist', 'mainWeather_Rain', 'mainWeather_Snow']
                    
                    # initialise a dict with the features as keys and None as values
                    features_and_values_dict = dict.fromkeys(features)
                    # give the corresponding keys the user input and weather forecast as values
                    # weekday_Friday and mainWeather_Clear were dropped during ML model training by encoding with dummies and dropping one of the resulting features
                    features_and_values_dict['temperature'] = temperature
                    features_and_values_dict['cloudiness'] = cloudiness
                    features_and_values_dict['windSpeed'] = wind_speed
                    features_and_values_dict['rain'] = rain
                    features_and_values_dict['snow'] = snow
                    features_and_values_dict['hour_sin'] = hour_sin
                    features_and_values_dict['hour_cos'] = hour_cos
                    if day_of_the_week_string != 'Friday':
                        features_and_values_dict[f'weekday_{day_of_the_week_string}'] = 1
                    if main_weather != 'Clear':
                        features_and_values_dict[f'mainWeather_{main_weather}'] = 1
                    # give the other features 0 as value
                    for k,v in features_and_values_dict.items():
                        if features_and_values_dict[k] == None:
                            features_and_values_dict[k] = 0
                    
                    # turns lists of mappings (dict-like objects) of feature names to feature values into Numpy arrays
                    v = DictVectorizer(sparse=False, sort=False)
                    new_sample_to_make_prediction = v.fit_transform(features_and_values_dict)

                    # predict availability for user input and weather forecast
                    availability_prediction_result = station_model.predict(new_sample_to_make_prediction)
                    availability_prediction = int(availability_prediction_result[0])

                    # return the weather forecast conditions and availability prediction to the frontend as a dictionary
                    return {time_requested_unix_timestamp:{"main weather":main_weather, "temperature":temperature, "cloudiness": cloudiness, "wind speed": wind_speed, "rain": rain, "snow": snow, "icon": weather_icon, "availability_prediction": availability_prediction}}
            return {"error": f"time requested didn't match available data: {hourly_weather_forecast['hourly']}"}    
    else:
        logging.error(f"Request to Openweather Forecast API failed with {weather_forecast_api_response.status_code}: {weather_forecast_api_response.reason}")
        abort(400)

