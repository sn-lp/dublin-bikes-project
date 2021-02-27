# dublin-bikes-project
This is a group project for the Software Engineering module to build a Dublin Bikes App.

## Unit Tests

The tests folder contains python unit tests.
To execute all the tests run the following command: `python3 -m unittest`
To execute only one specific test: `python3 -m unittest tests.'file_name'.'method_name'`


## Config File
To run the scripts in this repository, you will need to create a ``config.py`` file in the base of the directory and populate it will the relevant values as below:
```python
class Config:   
    JCDECAUX_API_KEY = ''   
    # Details from AWS RDS
    DB_USER = ''   
    DB_PASSWORD = ''    
    DB_SERVER = '' 
    DB_PORT = ''    
    DB_NAME = ''
```

## The database and data units

Our RDS has two main tables "stations" and "station_updates".

"stations" stores static data about all dublin bikes station's in Dublin.
"station_updates" stores dynamic data about bike occupancy/availability and the weather conditions for each station at a particular date and time (using UNIX timestamp).

### Weather Data Units

1) mainWeather: a string representing the main weather condition (e.g. 'Rain', 'Drizzle', 'Thunderstorm', etc.)
2) temperature: Celsius degrees 
3) cloudiness: %
4) windSpeed: meters/sec
5) rain: precipitation volume in mm
6) snow: snow volume in mm

Notes:
To get the temperature in Celsius we need to change the 'units' parameter when calling the Openweather API to be equal to 'metric'. The default unit for temperature is Kelvin.

e.g.:
http://api.openweathermap.org/data/2.5/onecall?lat={latitude}&lon={longitude}&units=metric

## Running the application
### Creating the conda environment
To run the web application and scraping script, we recommend creating a ``conda`` environment with the dependencies in ``requirements.txt``:
```bash
$ conda env -n comp30830 python=3.8
$ conda activate comp30830
$ pip install -r requirements.txt
```

### Running the scraping script
To run the scraping script in the background use the following command:
```bash
$ nohup python python_request_api_json.py &> scraping_run.log &
```
Any logging information and error messages will be available in ``scraping_run.log``

### Running the web application
To start the web application run:
```bash
$ python application.py
```
