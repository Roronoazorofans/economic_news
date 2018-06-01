# coding=utf-8
from . import news_blue
from flask import render_template, session, current_app, g, abort
from info.models import User, News
from info import constants, db
from info.utils.comment import user_login_data

@news_blue.route('/news_collect')
@user_login_data
def news_collect():
    pass




@news_blue.route('/detail/<int:news_id>')
@user_login_data
def news_detail(news_id):
    # 1. 装饰器形式获取用户信息
    # 通过g变量获取user信息
    user = g.user

    # 2. 封装函数的形式获取用户信息
    # from info.utils.comment import user_login_data
    # user = user_login_data()
    # 获取新闻点击排行信息
    news_clicks = []
    try:
        news_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    # 获取通过news_id新闻信息
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
    # 判断新闻是否查询到,后续会对404统一做一个404页面
    if not news:
        abort(404)

    news.clicks += 1
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

    # 判断是否收藏的逻辑
    # 1.默认未收藏
    # 2.只有用户登录了才判断是否收藏
    # 3.如果登录用户收藏了,将收藏标记重置为已收藏

    # 默认是未收藏
    is_collected = False
    if user:
        # 判断该登录用户是否收藏了该新闻
        if news in user.collection_news:
            is_collected = True


    context = {
        "user":user,
        "news_clicks":news_clicks,
        "news":news.to_dict(),
        "is_collected":is_collected
    }

    return render_template('news/detail.html',context=context)