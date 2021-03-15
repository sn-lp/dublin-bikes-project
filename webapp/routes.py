from flask import g, render_template, jsonify
from webapp import app
from sql_tables import Stations, StationUpdates
from sqlalchemy import insert, create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import sys

# read config option from command line and import config file
if sys.argv[1] == 'dev':
    from config_dev import Config
elif sys.argv[1] == 'backup':
    from config_backup import Config
else:
    exit("Invalid config file name. Please pass 'dev' or 'backup' as an argument")

devConfig = Config()
BIKES_API_KEY = devConfig.JCDECAUX_API_KEY
WEATHER_API_KEY = devConfig.OPENWEATHER_API_KEY
DB_USER = devConfig.DB_USER
DB_PASSWORD = devConfig.DB_PASSWORD
DB_SERVER = devConfig.DB_SERVER
DB_PORT = devConfig.DB_PORT
DB_NAME = devConfig.DB_NAME

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
