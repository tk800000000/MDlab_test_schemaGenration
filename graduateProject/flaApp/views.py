from flaApp import app


@app.route("/")
def index():
    return "HelloWorld"
