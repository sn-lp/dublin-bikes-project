from flask import render_template
from webapp import app

@app.route("/")
def index():
    return render_template('index.html')


@app.route("/predictions")
def predictions():
    return "This is our amazing prediction page"

