from flask import Flask

app = Flask(__name__)

if app.config["ENV"] == "backup":
    app.config.from_object("config.BackupConfig")
else:
    app.config.from_object("config.MainConfig")

# TODO: Document why we need this import down here
from webapp import routes
