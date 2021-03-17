from flask import Flask

app = Flask(__name__)

if app.config["ENV"] == "production":
    app.config.from_object("config.ProductionConfig")
elif app.config["ENV"] == "backup":
    app.config.from_object("config.BackupConfig")
else:
    app.config.from_object("config.DevelopmentConfig")

# TODO: Document why we need this import down here
from webapp import routes
