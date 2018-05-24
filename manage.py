# coding=utf-8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis


app = Flask(__name__)

# 创建配置文件
class Config(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/information_01"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

# 加载配置文件
app.config.from_object(Config)
# 创建连接到mysql数据库的对象
db = SQLAlchemy(app)
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
@app.route('/')
def index():
    return 'index page'


if __name__ == '__main__':
    redis_store.set("name", "zoro")
    app.run()
