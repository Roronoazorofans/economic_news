# coding=utf-8
from . import news_blue
from flask import render_template, session, current_app, g, abort, jsonify, request
from info.models import User, News, Comment, CommentLike
from info import constants, db, response_code
from info.utils.comment import user_login_data



@news_blue.route('/followed_user', methods=['POST'])
@user_login_data
def followed_user():
    """添加关注"""
    login_user = g.user
    if not login_user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg='用户未登录')
    # 获取参数
    user_id = request.json.get('user_id')
    action = request.json.get('action')
    # 校验参数
    if not all([user_id, action]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
    if action not in ['follow','unfollow']:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
    # 查询要添加关注的用户是否存在
    try:
        other = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询数据失败')
    if not other:
        return jsonify(errno=response_code.RET.NODATA, errmsg='用户不存在')

    if action == 'follow':
        if other not in login_user.followed:
            login_user.followed.append(other)
        else:
            return jsonify(errno=response_code.RET.DATAEXIST, errmsg='已关注')
    else:
        if other in login_user.followed:
            login_user.followed.remove(other)
        else:
            return jsonify(errno=response_code.RET.NODATA, errmsg='未关注')
    # 将要添加关注的用户同步到数据库
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='存储数据失败')
    # 返回结果
    return jsonify(errno=response_code.RET.OK, errmsg='操作成功')


# 评论点赞和取消点赞
@news_blue.route('/comment_like', methods=['POST'])
@user_login_data
def comment_like():
    # 接受用户登录信息
    user = g.user
    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg='用户未登录')
    # 接受请求参数
    comment_id = request.json.get('comment_id')
    news_id = request.json.get('news_id')
    action = request.json.get('action')
    # 校验参数
    if not all([comment_id, news_id, action]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
    if action not in ['add', 'remove']:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
    # 查询评论数据是否存在
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询评论数据失败')
    if not comment:
        return jsonify(errno=response_code.RET.NODATA, errmsg='评论不存在')

        # 要先查询是否点赞了,如果没有点赞才执行点赞操作
    comment_like_model = CommentLike.query.filter(CommentLike.user_id == user.id, CommentLike.comment_id == comment_id).first()
    # 当执行点赞操作时:
    if action == 'add':
        if not comment_like_model:
            # 创建模型对象添加属性
            comment_like_model = CommentLike()
            comment_like_model.user_id = user.id
            comment_like_model.comment_id = comment_id
            # 新增点赞
            db.session.add(comment_like_model)
            # 增加点赞条数
            comment.like_count += 1
    else:
        if comment_like_model:
            # 删除对象
            db.session.delete(comment_like_model)
            # 点赞数减1
            comment.like_count -= 1
    # 最后统一提交
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=response_code.RET.DBERR, errmsg='操作失败')
    return jsonify(errno=response_code.RET.OK, errmsg='操作成功')



# 新闻评论
@news_blue.route('/news_comment', methods=['POST'])
@user_login_data
def news_comment():
    """只有在用户登录的情况下才能进行评论操作

    """
    user = g.user.to_dict()
    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg='用户未登录')
    # 接收请求参数 1.被评论新闻id 2.评论内容
    news_id = request.json.get('news_id')
    comment_context = request.json.get("comment")
    parent_id = request.json.get('parent_id')
    # 校验参数
    # parent_id 非必要
    if not all([news_id, comment_context]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
    # 将news_id和parent_id(如果其存在)转成整型,目的是为了限制参数格式
    try:
        news_id = int(news_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
    # 查询新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询新闻数据失败')
    if not news:
        return jsonify(errno=response_code.RET.NODATA, errmsg='新闻不存在')

    # 创建评论对象
    comment = Comment()
    # 给评论对象赋值
    comment.user_id = user.id
    comment.news_id = news_id
    comment.content = comment_context
    if parent_id:
        comment.parent_id = parent_id
    # 将评论数据存储入数据库
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=response_code.RET.DBERR, errmsg='存储评论数据失败')
    return jsonify(errno=response_code.RET.OK, errmsg='ok', data=comment.to_dict())


@news_blue.route('/news_collect',methods=['POST'])
@user_login_data
def news_collect():
    """只有在用户登录下才能收藏
    1.获取登录用户信息，因为收藏和取消收藏都是需要在登录状态下执行的
    2.接受参数
    3.检验参数
    4.查询当前要收藏或取消收藏的新闻是否存在
    5.实现收藏和取消收藏
    6.响应收藏和取消收藏的结果
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

    # 添加是否关注状态
    is_followed = False

    if user and news.user:
        if news.user in user.followed:
            is_followed = True


    # 展示新闻评论数据
    # 根据新闻id查询该新闻的所有评论数据
    comments = []
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
    comment_like_ids = []
    if user:
        try:
            # 查询该用户点赞了哪些评论
            comment_likes = CommentLike.query.filter(CommentLike.user_id == user.id).all()
            comment_like_ids = [comment_like.comment_id for comment_like in comment_likes]
        except Exception as e:
            current_app.logger.error(e)
    comment_dict_list = []
    for comment in comments:
        # 给评论字典增加一个key,记录该评论是否被点赞
        comment_dict = comment.to_dict()
        # 默认未点赞
        comment_dict['is_like'] = False
        if comment.id in comment_like_ids:
            comment_dict['is_like'] = True
        comment_dict_list.append(comment.to_dict())
    context = {
        "user":user.to_dict() if user else None,
        "news_clicks":news_clicks,
        "news":news.to_dict(),
        "is_collected":is_collected,
        "comments":comment_dict_list,
        "is_followed": is_followed
    }

    return render_template('news/detail.html',context=context)