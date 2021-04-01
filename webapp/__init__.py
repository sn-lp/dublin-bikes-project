from flask import Flask

app = Flask(__name__)

if app.config["ENV"] == "backup":
    app.config.from_object("config.BackupConfig")
else:
    app.config.from_object("config.MainConfig")

# import is down here to avoid circular imports
from webapp import routes
