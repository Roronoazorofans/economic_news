# coding=utf-8
from . import index_blue
from flask import render_template, current_app
from info import redis_store
from info.models import User
from flask import session
@index_blue.route("/")
def index():
    """主页"""
    # 测试数据库
    # redis_store.set("name","zjg")

    # 1. 获取用户的状态保持信息，用于获取用户的登录信息
    user_id = session.get("user_id", None)
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
    # 2. 构造模板上下文
    context = {
        'user':user
    }

    # 主页渲染
    return render_template("news/index.html",context=context)

@index_blue.route("/favicon.ico", methods=["GET"])
def favicon():
    return current_app.send_static_file("news/favicon.ico")