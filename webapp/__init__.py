from flask import Flask

app = Flask(__name__)

if app.config["ENV"] == "production" or app.config["ENV"] == "development":
    app.config.from_object("config.MainConfig")
elif app.config["ENV"] == "backup":
    app.config.from_object("config.BackupConfig")


# TODO: Document why we need this import down here
from webapp import routes
