import requests
from config import MainConfig
import pytest

devConfig = MainConfig()
API_KEY = devConfig.JCDECAUX_API_KEY


def test_station_number_unique():
    # get all stations in dublin
    r = requests.get(
        f"https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey={API_KEY}"
    )
    if r.status_code == requests.codes.ok:
        stations_json = r.json()

        station_numbers_list = []
        for station in stations_json:
            # test if there aren't duplicate station numbers for contract=Dublin
            assert station["number"] not in station_numbers_list
            station_numbers_list.append(station["number"])
