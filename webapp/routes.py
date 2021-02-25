from webapp import app

@app.route("/")
def index():
    return "This is our amazing Dublin Bikes app"

@app.route("/predictions")
def predictions():
    return "This is our amazing prediction page"
