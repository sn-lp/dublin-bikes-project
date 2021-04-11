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
    sql_query_string = """
    SELECT
        stations.stationId,
        stations.name,
        stations.address,
        stations.latitude,
        stations.longitude,
        station_updates.totalStands,
        station_updates.availableBikes,
        station_updates.freeStands,
        station_updates.lastUpdate,
        station_updates.mainWeather,
        station_updates.temperature,
        station_updates.cloudiness,
        station_updates.windSpeed,
        station_updates.rain,
        station_updates.snow
    FROM stations
    LEFT JOIN station_updates
        ON stations.stationId = station_updates.stationId
    WHERE (station_updates.stationId, station_updates.lastUpdate)
        IN (SELECT stationId, max(lastUpdate) FROM station_updates GROUP BY stationId);
    """
    stations_with_availability = pd.read_sql(sql_query_string, g._database)
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
    station_latitude = request.args.get('stationLat')
    station_longitude = request.args.get('stationLong')
    time_requested_unix_timestamp = request.args.get('timeRequested')
    if not station_latitude or not station_longitude or not time_requested_unix_timestamp:
        abort(400)
    # convert timestamp to int type again (when it is passed as a query parameter it is a string)
    time_requested_unix_timestamp = int(time_requested_unix_timestamp)
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
                    # for now return the weather forecast conditions to the frontend as a dictionary
                    return {time_requested_unix_timestamp:{"main weather":main_weather, "temperature":temperature, "cloudiness": cloudiness, "wind speed": wind_speed, "rain": rain, "snow": snow, "icon": weather_icon}}
            return {"error": f"time requested didn't match available data: {hourly_weather_forecast['hourly']}"}    
    else:
        logging.error(f"Request to Openweather Forecast API failed with {weather_forecast_api_response.status_code}: {weather_forecast_api_response.reason}")
        abort(400)
    # TODO prediction part
