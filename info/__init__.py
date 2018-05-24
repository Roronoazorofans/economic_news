# coding=utf-8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from config import Config, configs



# 工厂方法创建app
def create_app(config_name):
    app = Flask(__name__)
    # 加载配置文件
    app.config.from_object(configs[config_name])
    # 创建连接到mysql数据库的对象
    db = SQLAlchemy(app)
    # 开启csrf保护
    CSRFProtect(app)
    Session(app)
    # 一定要注意返回app对象!!!
    return app