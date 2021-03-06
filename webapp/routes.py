from flask import g, render_template, jsonify
from webapp import app
from config import Config
from sql_tables import Stations, StationUpdates
from sqlalchemy import insert, create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd

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

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db

#@app.teardown_appcontext
#def close_connection(exception):
#    db = getattr(g, '_database', None)
#    if db is not None:
#        db.close()

@app.route("/stations")
def get_stations():
    engine = get_db()
    stations = pd.read_sql("SELECT * FROM stations", engine)
    availability = pd.read_sql("SELECT * FROM station_updates", engine)
    # Get the latest availability update for each station
    latest_availability = availability.sort_values("lastUpdate").groupby("stationId").tail(1)
    # Combine with static stations data
    stations_with_availability = stations.merge(latest_availability, on="stationId", how='inner')
    return stations_with_availability.to_json(orient="records")
