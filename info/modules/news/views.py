# coding=utf-8
from . import news_blue
from flask import render_template, session, current_app, g, abort, jsonify, request
from info.models import User, News
from info import constants, db, response_code
from info.utils.comment import user_login_data

@news_blue.route('/news_collect',methods=['POST'])
@user_login_data
def news_collect():
    """只有在用户登录下才能收藏

    """
    # 获取用户信息
    user = g.user
    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg='用户未登录')
    # 接受参数
    news_id = request.json.get("news_id")
    action = request.json.get("action")
    # 校验参数
    if not all([news_id, action]):
        return jsonify(errno=response_code.RET.NODATA, errmsg='缺少参数')
    if action not in ["collect","cancel_collect"]:
        return jsonify(errno=response_code.RET.DATAERR, errmsg='参数错误')
    # 查询当前要收藏的新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询新闻数据失败')

    if not news:
        return jsonify(errno=response_code.RET.NODATA, errmsg='新闻不存在')
    # 如果当前action为collect，只有当前新闻不在用户的收藏列表中，才执行收藏新闻
    if action == "collect":
        if news not in user.collection_news:
            user.collection_news.append(news)
    else:
        if news in user.collection_news:
            user.collection_news.remove(news)
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=response_code.RET.DBERR, errmsg='操作失败')
    return jsonify(errno=response_code.RET.OK, errmsg='OK')




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