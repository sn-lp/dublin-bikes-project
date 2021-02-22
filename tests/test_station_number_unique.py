import requests
from config import Config
import unittest

devConfig = Config()
API_KEY = devConfig.JCDECAUX_API_KEY

class TestUniqueStationNumber(unittest.TestCase):
    def test_duplicates(self): 
        # get all stations in dublin 
        r = requests.get(f"https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey={API_KEY}")
        if r.status_code == requests.codes.ok:
            stations_json = r.json()

            station_numbers_list = []
            for station in stations_json:
                # test if there aren't duplicate station numbers for contract=Dublin 
                self.assertNotIn(station['number'], station_numbers_list)
                station_numbers_list.append(station['number'])

if __name__ == '__name__':
    unittest.main()