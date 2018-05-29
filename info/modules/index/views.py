# coding=utf-8
from info import response_code
from . import index_blue
from flask import render_template, current_app, request, jsonify
from info import redis_store,constants
from info.models import User, News
from flask import session

@index_blue.route("/news_list")
def index_news_list():
    """提供主页新闻列表数据
    1. 获取参数：新闻分类id,当前展示第几页，每页展示多少条
    2. 校验参数，要求参数必须是整数
    3. 根据参数查询用户需要的数据，根据新闻发布时间倒序，最后实现分页
    4. 构造响应的新闻数据
    5. 响应新闻数据
    """
    # 1. 获取参数：新闻分类id,当前展示第几页，每页展示多少条,如果不传数据,就使用默认值
    cid = request.args.get("cid","1")
    page = request.args.get("page","1")
    per_page = request.args.get("per_page","10")

    # 2. 校验参数，要求参数必须是整数
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')

    if cid == 1:
        # 当传入的新闻分类是1，查询所有分类的新闻，根据新闻发布的时间倒序，分页
        paginate = News.query.order_by(News.create_time.desc()).paginate(page,per_page,False)
    else:
        # 当传入的新闻分类不是1，查询当前分类的新闻，根据新闻发布的时间倒序，分页
        paginate = News.query.filter(News.category_id==cid).order_by(News.create_time.desc()).paginate(page, per_page, False)
    # 4.构造响应的新闻数据
    # 4.1 获取paginate的模型对象
    news_list = paginate.items
    # 4.2 获取总页数：为了实现上拉刷新
    total_page = paginate.pages
    # 4.3 当前在第几页
    current_page = paginate.page
    # 将模型对象列表news_list转成字典列表

    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())

    # 构造新闻响应数据
    data = {
        "news_dict_list":news_dict_list,
        "total_page":total_page,
        "current_page":current_page
    }
    # 5. 响应新闻数据
    return jsonify(errno=response_code.RET.OK, errmsg='OK',data=data)




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