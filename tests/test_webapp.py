import pytest
import json
from webapp import app
import requests

def test_home_page():
    with app.test_client() as test_client:
        response = test_client.get('/')
        assert response.status_code == 200
        assert b"Group 5 Dublin Bikes App" in response.data

def test_stations():
    with app.test_client() as test_client:
        response = test_client.get("/stations")
        assert response.status_code == 200
        data = json.loads(response.data)

        # Check if there are any fields missing in any of the station data
        for station in data:
            assert "stationId" in station
            assert "name" in station
            assert "latitude" in station
            assert "longitude" in station
            assert "banking" in station
            assert "isOpen" in station
            assert "totalStands" in station
            assert "availableBikes" in station
            assert "freeStands" in station
            assert "lastUpdate" in station
            assert "mainWeather" in station
            assert "temperature" in station
            assert "cloudiness" in station
            assert "windSpeed" in station
            assert "rain" in station
            assert "snow" in station

def test_station_availability_history():
    with app.test_client() as test_client:
        # We should get a 400 error if we don't pass a stationId
        response = test_client.get("/availability_history")
        assert response.status_code == 400

        response = test_client.get("/availability_history?stationId=10")
        # We should have data for 7 days
        data = json.loads(response.data)
        assert len(data.keys()) == 7

        # Check that the data makes sense
        for day, hourly_data in data.items():
            assert int(day) >= 0 and int(day) <= 6
            for hour_data in hourly_data:
                assert hour_data["hour"] >= 0 and hour_data["hour"] <= 23
                assert hour_data["availableBikes"] >= 0

def test_station_available_spaces_history():
    with app.test_client() as test_client:
        # We should get a 400 error if we don't pass a stationId
        response = test_client.get("/available_spaces_history")
        assert response.status_code == 400

        response = test_client.get("/available_spaces_history?stationId=10")
        data = json.loads(response.data)
        # We should have data for 7 days
        assert len(data.keys()) == 7

        # Check that the data makes sense
        for day, hourly_data in data.items():
            assert int(day) >= 0 and int(day) <= 6
            for hour_data in hourly_data:
                assert hour_data["hour"] >= 0 and hour_data["hour"] <= 23
                assert hour_data["freeStands"] >= 0
