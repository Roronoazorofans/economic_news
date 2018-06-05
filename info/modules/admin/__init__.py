# coding=utf-8
from flask import Blueprint, session, redirect, url_for, request
admin_blue = Blueprint('admin',__name__,url_prefix='/admin')

from . import views

@admin_blue.before_request
def check_admin():
    """在每次请求前判断是否是管理员用户"""
    is_admin = session.get('is_admin', False)
    # 注意：当只加第一个条件时会在普通用户登录状态下把进入127.0.0.1/admin/login的入口也给封住,因为在请求之前也进行了判断，此时就需要加入第二个判断条件

    if not is_admin and not request.url.endswith('/admin/login'):
        return redirect(url_for('index.index'))