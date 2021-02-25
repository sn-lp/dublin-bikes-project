from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists
from sql_tables import Base
from config import Config

devConfig = Config()
DB_USER = devConfig.DB_USER
DB_PASSWORD = devConfig.DB_PASSWORD
DB_SERVER = devConfig.DB_SERVER
DB_PORT = devConfig.DB_PORT
DB_NAME = devConfig.DB_NAME

# connect to rds database
url = 'mysql+mysqlconnector://{}:{}@{}:{}'.format(DB_USER, DB_PASSWORD, DB_SERVER, DB_PORT)
engine = create_engine(url, echo=True)

# check if a database with name "DB_NAME" does not exist and create the database if it doesn't (testing purposes)
if not database_exists(url + "/" + DB_NAME):
    engine.execute("CREATE DATABASE " + DB_NAME)
engine.execute("USE " + DB_NAME)
    
# this creates both tables "stations" and "availability"
Base.metadata.create_all(engine)