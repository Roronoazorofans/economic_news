# coding=utf-8
from . import user_blue
from flask import render_template, g, redirect, url_for, request, current_app, jsonify, session
from info.utils.comment import user_login_data
from info import db, response_code


@user_blue.route('/base_info', methods=['GET','POST'])
@user_login_data
def base_info():
    user = g.user
    # 当用户查看用户中心时，此时为GET请求
    if request.method == 'GET':
        if user:
            context = {
                'user':user
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
    user = g.user
    # 如果用户未登录下自动跳转到主页面
    if not user:
        return redirect(url_for('index.index'))

    context = {
        'user':user
    }
    return render_template('news/user.html', context=context)