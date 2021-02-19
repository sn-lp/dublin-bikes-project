from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists
from sql_tables import Base

# use your database details here
user = ""
password = ""
server = "your database endpoint"
port = ""

# connect to rds database
url = 'mysql+mysqlconnector://{}:{}@{}:{}'.format(user, password, server, port)
engine = create_engine(url, echo=True)

dbname = "dublin_bikes"

# check if a database with name "database name" does not exist and create the database if it doesn't (testing purposes)
if not database_exists(url + "/" + dbname):
    engine.execute("CREATE DATABASE " + dbname)
engine.execute("USE " + dbname)
    
# this creates both tables "stations" and "availability"
Base.metadata.create_all(engine)