'''
this defines the sql tables which should be useful to create tables 
but also to make queries to read/insert/update/delete rows from the tables in the database
'''

from sqlalchemy import create_engine, Table, Column, Integer, String, TIMESTAMP, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Stations(Base):
    __tablename__ = "stations"
    # stationId is station['number'] returned by the API after checking that there are no duplicates for contract=Dublin
    stationId = Column(Integer, primary_key = True)
    name = Column(String(100), nullable = False)
    address = Column(String(100), nullable = False)
    latitude = Column(Float, nullable = False)
    longitude = Column(Float, nullable = False)
    banking = Column(Boolean, nullable = False)
    isOpen = Column(Boolean, nullable = False)

class Availability(Base):
    __tablename__ = "availability"
    stationId = Column(Integer, ForeignKey(Stations.stationId), primary_key = True)
    '''
    we are including totalStands in here and not in 'Stations' since in the API it belongs to "Dynamic Data" 
    and there's the possibility the number might change --> a stand added or removed
    '''
    totalStands = Column(Integer, nullable = False)
    availableBikes = Column(Integer, nullable = False)
    freeStands = Column(Integer, nullable = False)
    lastUpdate = Column(TIMESTAMP, nullable = False, primary_key = True)