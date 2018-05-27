# coding=utf-8
from . import index_blue
from flask import render_template, current_app
from info import redis_store
@index_blue.route("/")
def index():
    """主页"""
    # 测试数据库
    # redis_store.set("name","zjg")

    # 主页渲染
    return render_template("news/index.html")

@index_blue.route("/favicon.ico", methods=["GET"])
def favicon():
    return current_app.send_static_file("news/favicon.ico")