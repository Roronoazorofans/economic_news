# coding=utf-8
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template,g
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import csrf
from flask_wtf.csrf import CSRFProtect
from redis import StrictRedis
from config import configs



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

redis_store = None

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
    global redis_store
    redis_store = StrictRedis(host=configs[config_name].REDIS_HOST, port=configs[config_name].REDIS_PORT,decode_responses=True)
    # 开启csrf保护
    CSRFProtect(app)
    # 业务一开始就准备请求钩子，在每次的请求结束后向浏览器写入cookie
    @app.after_request
    def after_request(response):
        # 生成csrf随机值
        csrf_token = csrf.generate_csrf()
        response.set_cookie('csrf_token', csrf_token)
        return response

    from info.utils.comment import user_login_data
    @app.errorhandler(404)
    @user_login_data
    def page_not_found(e):
        user = g.user
        if user:
            context = {
                'user': user.to_dict() if user else None
            }
            return render_template('news/404.html', context=context)

    # 将自定义过滤器函数, 转成模板中可以直接使用的过滤器
    from info.utils.comment import do_rank
    app.add_template_filter(do_rank, "rank")



    Session(app)
    # 哪里注册蓝图就在哪里导入,避免导入时模块不存在
    from info.modules.index import index_blue
    # 将蓝图注册到app
    app.register_blueprint(index_blue)
    # 将用户模块的蓝图导入
    from info.modules.passport import passport_blue
    # 将蓝图注册到app
    app.register_blueprint(passport_blue)
    from info.modules.news import news_blue
    app.register_blueprint(news_blue)
    from info.modules.user import user_blue
    app.register_blueprint(user_blue)
    from info.modules.admin import admin_blue
    app.register_blueprint(admin_blue)

    # 一定要注意返回app对象!!!
    return app