from flask import g, render_template, jsonify, request, abort
from webapp import app
from sql_tables import Stations, StationUpdates
from sqlalchemy import insert, create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import sys

DB_USER = app.config["DB_USER"]
DB_PASSWORD = app.config["DB_PASSWORD"]
DB_SERVER = app.config["DB_SERVER"]
DB_PORT = app.config["DB_PORT"]
DB_NAME = app.config["DB_NAME"]

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
    return "This is our amazing prediction page"

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
