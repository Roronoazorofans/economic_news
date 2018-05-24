# coding=utf-8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session


app = Flask(__name__)

# 创建配置文件
class Config(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/information_01"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    # 配置csrf秘钥 使用一组随机数作为'盐'
    SECRET_KEY = "q7pBNcWPgmF6BqB6b5VICF7z7pI+90o0O4CaJsFGjzRsYiya9SEgUDytXvzFsIaR"
    # 配置session数据
    # 配置存储session数据的数据库类型为redis
    SESSION_TYPE = "redis"
    # 开启用户签名
    SESSION_USE_SIGNER = True
    # 设置session有效期 为一天
    PERNAMENT_SESSION_LIFETIME = 3600*24

# 加载配置文件
app.config.from_object(Config)
# 创建连接到mysql数据库的对象
db = SQLAlchemy(app)
# 开启csrf保护
CSRFProtect(app)
Session(app)


redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
@app.route('/')
def index():
    return 'index page'


if __name__ == '__main__':
    redis_store.set("name", "zoro")
    app.run()
