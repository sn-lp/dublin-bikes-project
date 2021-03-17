from flask import g, render_template, jsonify
from webapp import app
from sql_tables import Stations, StationUpdates
from sqlalchemy import insert, create_engine
from sqlalchemy.orm import sessionmaker

DB_USER = app.config["DB_USER"]
DB_PASSWORD = app.config["DB_PASSWORD"]
DB_SERVER = app.config["DB_SERVER"]
DB_PORT = app.config["DB_PORT"]
DB_NAME = app.config["DB_NAME"]

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
