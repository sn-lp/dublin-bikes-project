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
