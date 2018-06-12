# coding=utf-8
from . import user_blue
from flask import render_template, g, redirect, url_for, request, current_app, jsonify, session,abort
from info.utils.comment import user_login_data
from info import db, response_code, constants
from info.utils.captcha.file_storage import upload_file
from info.models import News, Category


@user_blue.route('/user_follow')
@user_login_data
def user_follow():
    """我的关注"""
    user = g.user
    # 接受参数
    page = request.args.get('p', '1')
    # 校验参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
        # 查询该用户的关注用户
    follows_list = []
    total_page = 1
    current_page = 1
    try:
        paginate = user.followed.paginate(page, constants.USER_FOLLOWED_MAX_COUNT,False)
        follows_list = paginate.items
        total_page = paginate.pages
        current_page = paginate.page
    except Exception as e:
        current_app.logger.error(e)
        abort(404)
    follows_dict_list = []
    for follows in follows_list:
        follows_dict_list.append(follows.to_dict())

    context = {
        'users': follows_dict_list,
        'total_page': total_page,
        'current_page': current_page
    }

    return render_template('news/user_follow.html', context=context)








@user_blue.route('/news_list')
@user_login_data
def news_list():
    """用户新闻列表"""
    user = g.user
    if not user:
        return redirect(url_for('index.index'))
    # 1. 接受参数(page)
    page = request.args.get('p','1')
    # 2. 校验参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = '1'
    # 3. 查询登录登录用户发布的新闻，并进行分页
    paginate = None
    try:
        paginate = News.query.filter(News.user_id == user.id).paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
    except Exception as e:
        current_app.logger.error(e)

    # 3. 构造响应数据
    news_list = paginate.items
    total_page = paginate.pages
    current_page = paginate.page

    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_review_dict())

    context = {
        'news_list':news_dict_list,
        'total_page':total_page,
        'current_page':current_page
    }
    # 4.渲染模板
    return render_template('news/user_news_list.html', context=context)





@user_blue.route('/news_release', methods=['GET','POST'])
@user_login_data
def news_release():
    """新闻发布"""
    user = g.user
    if not user:
        return redirect(url_for('index.index'))
    if request.method == 'GET':
        # 展示全部分类(不包含最新)
        categories = Category.query.all()
        # 将‘最新’删除
        categories.pop(0)
        # 构造响应数据
        context = {
            'categories': categories
        }
        # 渲染模板
        return render_template('news/user_news_release.html', context=context)
    if request.method == 'POST':
        # 1. 接受参数(title,category_id,digest,index_image,content)
        title = request.form.get('title')
        source = '个人发布'
        category_id = request.form.get('category_id')
        digest = request.form.get('digest')
        index_image = request.files.get('index_image')
        content = request.form.get('content')
        # 2. 校验参数
        if not all([title,category_id,digest,index_image,content]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数有误')
        # 尝试读取图片
        try:
            index_image = index_image.read()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数有误')
        # 将图片上传到七牛云
        try:
            key = upload_file(index_image)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数有误')
        # 3.将新闻数据储存到数据库
        # 创建新闻对象,并添加属性
        news = News()
        news.title = title
        news.source = source
        news.category_id = category_id
        news.digest = digest
        # 此处必须自己添加url实乃迫不得已,因为新闻网站大部分图片都是爬取的
        news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
        news.content = content
        news.user_id = user.id
        news.status = 1

        try:
            db.session.add(news)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg='存储数据失败')

        return jsonify(errno=response_code.RET.OK, errmsg='新闻发布成功,等待审核')


@user_blue.route('/user_collection')
@user_login_data
def user_collection():
    """用户收藏"""
    user = g.user
    if not user:
        return redirect(url_for('index.index'))
    # 1.接受参数
    # 当前查看第几页,如果不传默认是第1页
    page = request.args.get('p','1')
    # 2.校验参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = '1'


    # 3.查询当前用户的收藏新闻并分页显示
    paginate = user.collection_news.paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)

    # 4.构造响应数据
    news_list = paginate.items
    total_page = paginate.pages
    current_page = paginate.page
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())
    context = {
        'news_list': news_dict_list,
        'total_page': total_page,
        'current_page': current_page
    }

    return render_template('news/user_collection.html', context=context)


@user_blue.route('/pass_info', methods=['GET','POST'])
@user_login_data
def pass_info():
    user = g.user
    #  修改密码
    if request.method == 'GET':
        if user:
            return render_template('news/user_pass_info.html')
        else:
            return redirect(url_for('index.index'))
    if request.method == 'POST':
        if user:
            # 1.接受参数(原密码, 新密码)
            old_password = request.json.get('old_password')
            new_password = request.json.get('new_password')
            # 2.校验参数(参数是否齐全,校验原密码是否正确)
            if not all([old_password, new_password]):
                return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
            if not user.check_passowrd(old_password):
                return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
            # 3.修改模型对象属性
            user.password = new_password
            # 4.将新密码存储到数据库
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(errno=response_code.RET.DBERR, errmsg='存储到数据库失败')
            # TODO: 清除session
            # 5.响应结果
            return jsonify(errno=response_code.RET.OK, errmsg='修改密码成功')


@user_blue.route('/pic_info', methods=['GET','POST'])
@user_login_data
def pic_info():
    user = g.user
    if request.method == 'GET':
        if user:
            context = {
                'user':user.to_dict()
            }
            return render_template('news/user_pic_info.html', context=context)
    if request.method == 'POST':
        if user:
            # 1.获取到上传的文件
            try:
                avartar_file = request.files.get("avatar").read()
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=response_code.RET.PARAMERR, errmsg='读取文件错误')

            # 2.再将文件上传到七牛云
            try:
                key = upload_file(avartar_file)
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=response_code.RET.THIRDERR, errmsg='上传图片错误')
            # 3.将头像信息更新到用户模型中
            user.avatar_url = key
            # 4.将存储在七牛云的唯一图片标识url存入数据库中
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(errno=response_code.RET.DBERR, errmsg='存储图片数据失败')

            # 构造响应数据, 上传头像结束后直接刷新当前头像
            data = {
                "avatar_url": constants.QINIU_DOMIN_PREFIX + key
            }

            # 返回结果
            return jsonify(errno=response_code.RET.OK, errmsg='上传成功', data=data)


@user_blue.route('/base_info', methods=['GET','POST'])
@user_login_data
def base_info():
    user = g.user
    # 当用户查看用户中心时，此时为GET请求
    if request.method == 'GET':
        if user:
            context = {
                'user':user.to_dict()
            }
            return render_template('news/user_base_info.html', context=context)

    # 当用户修改个人中心数据时，此时为POST请求
    if request.method == 'POST':
        if user:
            # 1. 接受请求数据
            nick_name = request.json.get("nick_name")
            signature = request.json.get("signature")
            gender = request.json.get("gender")
            # 2. 校验数据
            if not all([nick_name, signature, gender]):
                return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
            if gender not in ['MAN', 'WOMAN']:
                return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
            # 3. 修改模型对象属性值
            user.nick_name = nick_name
            user.signature = signature
            user.gender = gender
            # 4. 提交到数据库
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(errno=response_code.RET.DBERR, errmsg='存储数据失败')

            # 5. 修改当前状态保持数据里面的nick_name值
            session['nick_name'] = nick_name

            # 返回结果
            return jsonify(errno=response_code.RET.OK, errmsg='修改数据成功')


@user_blue.route('/info')
@user_login_data
def user_info():
    """个人中心入口
    1. 必须在登录状态下才能进入个人中心
    """
    user = g.user
    # 如果用户未登录下自动跳转到主页面
    if not user:
        return redirect(url_for('index.index'))

    context = {
        'user':user.to_dict()
    }
    return render_template('news/user.html', context=context)