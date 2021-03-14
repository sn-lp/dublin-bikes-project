from flask import g, render_template, jsonify
from webapp import app
from sql_tables import Stations, StationUpdates
from sqlalchemy import insert, create_engine
from sqlalchemy.orm import sessionmaker

# read config option from command line and import config file
if len(sys.argv) != 2:
    sys.exit("Invalid config file name. Please pass 'dev' or 'backup' as an argument")
elif sys.argv[1] == 'dev':
    from config_dev import Config
elif sys.argv[1] == 'backup':
    from config_backup import Config


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
    data = []
    rows = engine.execute("SELECT stationId, latitude, longitude FROM stations")
    for row in rows:
        data.append(dict(row))
    return jsonify(available=data)
