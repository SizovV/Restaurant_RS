from flask import Flask
from flask import render_template

app = Flask(__name__) # application 'app' is object of class 'Flask'

# import files
# home page
@app.route('/')  # root : main page
def index():
    # by default, 'render_template' looks inside the folder 'template'
    return "fsd"

if __name__ == '__main__':
    # '0.0.0.0' = 127.0.0.1 i.e. localhost
    # port = 5000 : we can modify it for localhost
    app.run() # local webserver : app.run()