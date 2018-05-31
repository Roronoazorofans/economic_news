# coding=utf-8
from . import news_blue
from flask import render_template

@news_blue.route('/detail/<int:news_id>')
def news_detail(news_id):
    context = {

    }

    return render_template('news/detail.html',context=context)