# coding=utf-8
from . import index_blue
from flask import render_template, current_app
from info import redis_store,constants
from info.models import User, News
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
    # 2. 获取新闻点击排行数据
    news_clicks = None
    try:
        news_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    # 构造模板上下文
    context = {
        'user':user,
        'news_clicks':news_clicks
    }

    # 主页渲染
    return render_template("news/index.html",context=context)

@index_blue.route("/favicon.ico", methods=["GET"])
def favicon():
    return current_app.send_static_file("news/favicon.ico")