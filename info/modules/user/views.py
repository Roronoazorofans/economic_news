# coding=utf-8
from . import user_blue
from flask import render_template



@user_blue.route('/base_info',methods=['GET','POST'])
def base_info():

    return render_template('news/user_base_info.html')



@user_blue.route('/info', methods=['GET','POST'])
def user_info():
    context = {

    }
    return render_template('news/user.html', context=context)