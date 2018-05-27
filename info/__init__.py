# coding=utf-8
from logging.handlers import RotatingFileHandler
from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from config import configs
import logging
from info.modules.index import index_blue

# 对全局db的处理,请看SQLAlchemy源代码
# 创建SQLAlchemy对象
db = SQLAlchemy()

# 封装日志建立的方法
def setuplogging(level):
    # 设置日志的记录等级
    logging.basicConfig(level=level) # 调试debug级
    # 创建日志记录器，指明⽇志保存的路径、每个日志⽂件的最⼤大小、保存的⽇志⽂件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
    # 创建日志记录的格式 ⽇志等级 输⼊日志信息的⽂件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置⽇志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志⼯具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


# 工厂方法创建app
def create_app(config_name):
    app = Flask(__name__)
    # 在调用create_app方法时执行创建日志的方法  注意参数传入对应的等级level
    setuplogging(configs[config_name].LOGGING_LEVEL)
    # 加载配置文件
    app.config.from_object(configs[config_name])
    # # 创建连接到mysql数据库的对象
    # db = SQLAlchemy(app)
    db.init_app(app)
    # 开启csrf保护
    CSRFProtect(app)
    Session(app)

    # 将蓝图注册到app
    app.register_blueprint(index_blue)
    # 一定要注意返回app对象!!!
    return app