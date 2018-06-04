# coding=utf-8
from . import user_blue
from flask import render_template, g, redirect, url_for, request, current_app, jsonify, session
from info.utils.comment import user_login_data
from info import db, response_code, constants
from info.utils.captcha.file_storage import upload_file

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