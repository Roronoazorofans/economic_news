# coding=utf-8
from . import index_blue
from info import redis_store
@index_blue.route("/")
def index():
    """主页"""
    # 测试数据库
    redis_store.set("name","zjg")

    return "index"