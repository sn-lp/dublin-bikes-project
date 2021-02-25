from flask import Flask

app = Flask(__name__)

# TODO: Document why we need this import down here
from webapp import routes
