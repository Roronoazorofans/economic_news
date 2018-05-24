# coding=utf-8
from flask import Flask

app = Flask(__name__)

class Config(object):
    DEBUG = True


app.config.from_object(Config)

@app.route('/')
def index():
    return 'index page'


if __name__ == '__main__':
    app.run()
