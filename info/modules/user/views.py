# coding=utf-8
from . import user_blue
from flask import render_template, g
from info.utils.comment import user_login_data


@user_blue.route('/base_info',methods=['GET','POST'])
def base_info():

    return render_template('news/user_base_info.html')



@user_blue.route('/info', methods=['GET','POST'])
@user_login_data
def user_info():
    user = g.user


    context = {
        'user':user
    }
    return render_template('news/user.html', context=context)