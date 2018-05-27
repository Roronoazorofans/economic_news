# coding=utf-8
from . import index_blue
from flask import render_template
from info import redis_store
@index_blue.route("/")
def index():
    """主页"""
    # 测试数据库
    # redis_store.set("name","zjg")

    # 主页渲染
    return render_template("news/index.html")

@index_blue.route("/favicon.ico")
def favicon():
    return render_template("news/favicon.ico")