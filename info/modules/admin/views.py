# coding=utf-8
from info.modules.admin import admin_blue
from flask import render_template,request, current_app, session, redirect, url_for, g
from info.models import User
from info.utils.comment import user_login_data
import time,datetime

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

    # 2.用户月新增数 从6月1日算起 2018-06-01
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

    # 3. 用户日新增数




    context = {
        'total_count': total_count,
        'month_count': month_count

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