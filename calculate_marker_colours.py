"""
This script uses all of the historical data we have collected and calculates what the ranges of percentage bike availability should be to ensure an approximately
equal distribution of stations in each of the three colour groups (red, yellow, green)
"""
from sqlalchemy import create_engine
import pandas as pd
from config import Config

devConfig = Config()
DB_USER = devConfig.DB_USER
DB_PASSWORD = devConfig.DB_PASSWORD
DB_SERVER = devConfig.DB_SERVER
DB_PORT = devConfig.DB_PORT
DB_NAME = devConfig.DB_NAME

db_url = 'mysql+mysqlconnector://{}:{}@{}:{}/{}'.format(DB_USER, DB_PASSWORD, DB_SERVER, DB_PORT, DB_NAME)
engine = create_engine(db_url, echo=False)
database = engine.connect()

latest_availability = pd.read_sql("SELECT * FROM station_updates", database)

# What is the percentage of available bikes out of total stands in this station at this moment?
latest_availability['availability_percentage'] = latest_availability['availableBikes'] / latest_availability['totalStands']
print(latest_availability)

# Break the data into three equally sized groups
print(pd.qcut(latest_availability['availability_percentage'], 3))
