# coding=utf-8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from config import Config

app = Flask(__name__)

# 加载配置文件
app.config.from_object(Config)
# 创建连接到mysql数据库的对象
db = SQLAlchemy(app)
# 开启csrf保护
CSRFProtect(app)
Session(app)