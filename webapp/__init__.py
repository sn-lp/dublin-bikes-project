from flask import Flask
from config_dev import Config

app = Flask(__name__)
# loads the configuration from the config_dev module
app.config.from_object(Config)
# overrides values with the contents of the file the CONFIG_SETTINGS environment variable points to
app.config.from_envvar('CONFIG_SETTINGS')

# TODO: Document why we need this import down here
from webapp import routes
