# dublin-bikes-project

This is a group project for the Software Engineering module of the UCD 2020-2021 MSc/HDip in Computer Science (Conversion).

In this project we built a Web App that uses the JCDecaux public API to display the `Dublin Bikes` stations and availability in Dublin, Ireland.

The Web App provides user interactivity by implementing some features that allow the user to engage with it to search stations, get availability/occupancy information and plan a journey for a particular day and time.

Our app also uses other public APIs like Google Maps Javascript API and the Openweathermap API.

The app also has an implementation of Machine Learning techniques to train a model per station to predict the number of available bikes for a certain day, time and weather forecast conditions. This is achieved through applying a regression Random Forest algorithm on historical data collected over the course of the project.

## App main features

- search stations on map
- view most up to date availability information
- view hourly availability trends per station over the course of a week
- get availability prediction and weather forecast for a particular day, time and station

## Unit Tests

The tests folder contains python unit tests.
To execute all the tests run the following command: `python3 -m pytest`
To execute only one specific test: `python3 -m pytest tests.'file_name'.'method_name'`

## Config File

To run the scripts in this repository, you will need to create a `config.py` file in the base of the directory and populate it will the relevant values as below:

```python
class MainConfig(object):
    # APIs
    JCDECAUX_API_KEY = ''
    OPENWEATHER_API_KEY = ''
    GOOGLE_API = ''
    # DB details
    DB_USER = ''
    DB_PASSWORD = ''
    DB_SERVER = ''
    DB_PORT = ''
    DB_NAME = ''
    # S3 bucket
    S3_BUCKET = ''

class BackupConfig(MainConfig):
    # APIs
    JCDECAUX_API_KEY = ''
    OPENWEATHER_API_KEY = ''
    GOOGLE_API = ''
    # DB details
    DB_USER = ''
    DB_PASSWORD = ''
    DB_SERVER = ''
    DB_PORT = ''
    DB_NAME = ''
    # S3 bucket
    S3_BUCKET = ''
```

## The database and data units

Our RDS has two main tables "stations" and "station_updates".

"stations" stores static data about all dublin bikes station's in Dublin.
"station_updates" stores dynamic data about bike occupancy/availability and the weather conditions for each station at a particular date and time (using UNIX timestamp).

### Weather Data Units

1. mainWeather: a string representing the main weather condition (e.g. 'Rain', 'Drizzle', 'Thunderstorm', etc.)
2. temperature: Celsius degrees
3. cloudiness: % percentage
4. windSpeed: meters/sec
5. rain: precipitation volume in mm, for the last hour
6. snow: snow volume in mm, for the last hour

Notes:
To get the temperature in Celsius we need to change the 'units' parameter when calling the Openweathermap API to be equal to 'metric'. The default unit for temperature is Kelvin.

e.g.:
`http://api.openweathermap.org/data/2.5/onecall?lat={latitude}&lon={longitude}&units=metric&appid={api_key}`

## Running the application

### Creating the conda environment

To run the web application and scraping script, we recommend creating a `conda` environment with the dependencies in `requirements.txt`:

```bash
$ conda env -n comp30830 python=3.8
$ conda activate comp30830
$ pip install -r requirements.txt
```

### Running the scraping script

To run the scraping script in the background use the following command:

```bash
$ nohup python python_request_api_json.py &> nohup-dublin-bikes.log &
```

Any logging information and error messages will be available in `nohup-dublin-bikes.log`

### Running the web application

To start the web application run:

```bash
$ python application.py
```

## Exporting files to S3

To run the export script in the background use the following command:

```bash
$ nohup python export_to_s3.py &> export_to_s3.log &
```

Any logging information and error messages will be available in `export_to_s3.log`

## Code Linting

We use `prettier` to lint frontend code (Javascript, HTML and CSS)
To run `prettier`:

- Install node.js and npm (https://nodejs.org/en/ v14) (they come in the same installer);
- Run `npm install -g prettier`
- `sudo` might be needed to have write permissions
- Run `prettier --write .` on the project folder

We use `black` to lint backend code (Python) and it is in `requirements.txt`
Tu run `black`:

- Run `black .`

Both `prettier` and `black` are running in a CI pipeline for every Pull Request using GitHub actions.
