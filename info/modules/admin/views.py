# coding=utf-8
from info.modules.admin import admin_blue
from flask import render_template

@admin_blue.route('/login')
def admin_login():

    return render_template('admin/login.html')