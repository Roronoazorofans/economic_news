# coding=utf-8
from info.modules.admin import admin_blue
from flask import render_template,request,current_app,session,redirect,url_for,g,abort,jsonify
from info.models import User, News, db, Category
from info.utils.comment import user_login_data
import time,datetime
from info import constants,response_code
from info.utils.captcha.file_storage import upload_file


@admin_blue.route('/news_edit_detail/<int:news_id>', methods=['GET','POST'])
def news_edit_detail(news_id):
    if request.method == 'GET':
        news = None
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            abort(404)
        if not news:
            abort(404)

        categories = []
        try:
            categories = Category.query.all()
            categories.pop(0)
        except Exception as e:
            current_app.logger.error(e)
            abort(404)
        context = {
            'news': news,
            'categories': categories
        }

        return render_template('admin/news_edit_detail.html', context=context)

    if request.method == 'POST':
        # 1.获取参数
        title = request.form.get('title')
        category_id = request.form.get('category_id')
        digest = request.form.get('digest')
        index_image = request.files.get('index_image')
        content = request.form.get('content')
        # 2.校验参数
        if not all([title,category_id,digest,content]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
        # 3.查询要编辑的新闻
        news = None
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            abort(404)
        if not news:
            abort(404)
        # 4.上传图片到七牛云
        if index_image:
            try:
                index_image = index_image.read() # 读取图片数据为二进制数据
            except Exception as e:
                current_app.logger.error(e)
                abort(404)
            try:
                key = upload_file(index_image)
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=response_code.RET.THIRDERR, errmsg='上传失败')
            news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
        # 5.存储到数据库
        news.title = title
        news.category_id = category_id
        news.digest = digest
        news.content = content

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg='存储到数据库失败')

        return jsonify(errno=response_code.RET.OK, errmsg='操作成功')


@admin_blue.route('/news_edit')
def news_edit():
    # 获取参数
    page = request.args.get('p','1')
    key_word = request.args.get('keyword')
    try:
        page = int(page)
    except Exception as e:
        page = 1
    # 查询审核通过的新闻
    news_list = []
    total_page = 1
    current_page = 1
    try:
        if key_word:
            paginate = News.query.filter(News.status == 0, News.title.contains(key_word)).order_by(News.create_time.desc()).paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)
        else:
            paginate = News.query.filter(News.status == 0).order_by(News.create_time.desc()).paginate(page,constants.ADMIN_NEWS_PAGE_MAX_COUNT,False)
        # 构造响应数据
        news_list = paginate.items
        total_page = paginate.pages
        current_page = paginate.page
    except Exception as e:
        current_app.logger.error(e)
        abort(404)
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_dict())
    context = {
        'news_list':news_dict_list,
        'total_page':total_page,
        'current_page':current_page
    }
    return render_template('admin/news_edit.html', context=context)





@admin_blue.route('/news_review_detail/<int:news_id>', methods=['GET','POST'])
def news_review_detail(news_id):
    if request.method == 'GET':
        # 1. 接受参数
        # 2. 根据参数查询新闻
        news = None
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            abort(404)
        if not news:
            abort(404)
        #
        context = {
            'news': news.to_dict()

        }

        return render_template('admin/news_review_detail.html', context=context)
    if request.method == 'POST':
        # 1. 接受参数
        action = request.json.get('action')
        # 2. 校验参数
        if not action:
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
        if action not in ['accept','reject']:
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
        # 3. 查询要审核的新闻是否存在
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg='查询数据失败')
        if not news:
            return jsonify(errno=response_code.RET.NODATA, errmsg='查询的新闻不存在')

        # 3.判断action
        # 3.1 如果审核通过
        if action == 'accept':
            # 将status置为0
            news.status = 0
        # 审核不通过
        else:
            news.status = -1
            # 保存拒绝的理由
            reason = request.json.get('reason')
            if not reason:
                return jsonify(errno=response_code.RET.PARAMERR, errmsg='请填写拒绝通过原因')
            news.reason = reason
        # 上传到数据库
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg='存储数据失败')
        return jsonify(errno=response_code.RET.OK, errmsg='操作成功')








@admin_blue.route('/news_review')
def news_review():
    """新闻审核"""
    # 1. 接受参数
    page = request.args.get('p','1')
    keyword = request.args.get('keyword') # 关键字查询参数接收
    # 2. 校验参数
    try:
        page = int(page)
    except Exception as e:
        page = 1
    # 3. 查询所有除审核通过的新闻并分页展示
    news_list = []
    total_page = 1
    current_page = 1
    try:
        if keyword:
            paginate = News.query.filter(News.status != 0, News.title.contains(keyword)).order_by(News.create_time.desc()).paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)
        else:
            paginate = News.query.filter(News.status != 0).order_by(News.create_time.desc()).paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)
        news_list = paginate.items
        total_page = paginate.pages
        current_page = paginate.page
    except Exception as e:
        current_app.logger.error(e)
        abort(404)
    # 4. 构造响应数据

    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_review_dict())

    context = {
        'news_list': news_dict_list,
        'total_page': total_page,
        'current_page': current_page
    }

    return render_template('admin/news_review.html', context=context)





@admin_blue.route('/user_list')
def user_list():
    """用户列表"""
    # 查询用户列表并按照最后一次登录时间倒序分页展示
    page = request.args.get('p','1')
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    paginate = None
    try:
        user_actives = User.query.filter(User.is_admin==False).order_by(User.last_login.desc())
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/user_list.html', errmsg='查询用户数据失败')
    if user_actives:
        paginate = user_actives.paginate(page, constants.ADMIN_USER_PAGE_MAX_COUNT, False)
    # 构造响应数据
    user_active_list = paginate.items
    total_page = paginate.pages
    current_page = paginate.page
    user_active_dict_list = []
    for user in user_active_list:
        user_active_dict_list.append(user.to_admin_dict() if user_active_list else None)

    context = {
        'users': user_active_dict_list,
        'total_page': total_page,
        'current_page': current_page
    }

    return render_template('admin/user_list.html', context=context)





@admin_blue.route('/user_count')
def user_count():
    """用户统计量展示"""
    # 1.统计用户总数
    total_count = 0
    try:
        # 管理员不在统计内
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)

    # 2.用户月新增数  创建日期大于 2018-06-01 0:00:00
    month_count = 0
    # 2.1 生成当地时间
    t = time.localtime()
    # 2.2 生成当前月份开始时间字符串
    month_begin = "%d-%02d-01" % (t.tm_year, t.tm_mon)
    # 2.3 生成当前月份开始时间对象
    month_begin_date = datetime.datetime.strptime(month_begin, '%Y-%m-%d')
    # 2.4 查询注册时间大于当前月份开始时间的数量
    try:
        month_count = User.query.filter(User.create_time > month_begin_date,User.is_admin==False).count()
    except Exception as e:
        current_app.logger.error(e)

    # 3. 用户日新增数  从2018-06-05 0:00:00 <= 注册日期 < 2018-06-05 24:00:00
    day_count = 0
    day_begin = "%d-%02d-%d" % (t.tm_year, t.tm_mon, t.tm_mday)
    day_begin_date = datetime.datetime.strptime(day_begin, '%Y-%m-%d')
    try:
        day_count = User.query.filter(User.create_time > day_begin_date, User.is_admin==False).count()
    except Exception as e:
        current_app.logger.error(e)

    # 4. 活跃用户数量图表展示
    # 定义空数组，保存数据
    active_date = []
    active_count = []
    # 查询今天开始的时间
    today_begin = '%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday)
    today_begin_date = datetime.datetime.strptime(today_begin, '%Y-%m-%d')
    # 计算31天以内的每天间隔
    for i in range(0, 31):
        # 计算一天开始
        begin_date = today_begin_date - datetime.timedelta(days=i)
        # 计算一天结束
        end_date = today_begin_date - datetime.timedelta(days=(i - 1))
        # 计算活跃量
        count = User.query.filter(User.is_admin == False, User.last_login >= begin_date, User.last_login < end_date).count()
        # 将数据封装到列表
        active_count.append(count)
        # 将时间对象转成时间字符串
        active_date.append(datetime.datetime.strftime(begin_date, '%Y-%m-%d'))
    # 反转⽇期和数量，保证时间线从左⾄至右递增
    active_count.reverse()
    active_date.reverse()

    context = {
        'total_count': total_count,
        'month_count': month_count,
        'day_count': day_count,
        'active_count': active_count,
        'active_date': active_date

    }
    return render_template('admin/user_count.html',context=context)




@admin_blue.route('/')
@user_login_data
def admin_index():
    user = g.user
    if not user:
        return redirect(url_for('admin.admin_login'))
    context = {
        'user':user.to_dict()
    }
    return render_template('admin/index.html', context=context)

@admin_blue.route('/login',methods=['GET','POST'])
def admin_login():
    """管理员用户登录"""
    if request.method == 'GET':
        user_id = session.get('user_id', None)
        is_admin = session.get('is_admin', False)
        if user_id and is_admin:
            return redirect(url_for('admin.admin_index'))
        return render_template('admin/login.html')
    if request.method == 'POST':
        # 1. 接受参数
        username = request.form.get('username')
        password = request.form.get('password')
        # 2. 校验参数
        if not all([username, password]):
            return render_template('admin/login.html', errmsg='参数不足')

        # 3. 校验用户名和密码是否正确
        try:
            user = User.query.filter(User.nick_name == username).first()
        except Exception as e:
            current_app.logger.error(e)
            return render_template('admin/login.html', errmsg='查询用户数据失败')
        if not user:
            return render_template('admin/login.html', errmsg='用户名或密码错误')
        if not user.check_passowrd(password):
            return render_template('admin/login.html', errmsg='用户名或密码错误')
        if not user.is_admin:
            return render_template('admin/login.html', errmsg='用户权限错误')

        # 4. 写入状态保持信息到session
        session['nick_name'] = user.nick_name
        session['mobile'] = user.mobile
        session['is_admin'] = user.is_admin
        session['user_id'] = user.id


        # 5. 如果校验通过即进入管理员主界面
        return redirect(url_for('admin.admin_index'))