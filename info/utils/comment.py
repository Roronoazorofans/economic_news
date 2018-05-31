# coding=utf-8

from flask import session, current_app, g
from info.models import User
from functools import wraps


# 公共的工具文件
def do_rank(index):
    # 根据传入的索引,返回first, second, third
    if index == 1:
        return "first"
    elif index == 2:
        return "second"
    elif index == 3:
        return "third"
    else:
        return " "


# view_func == news_detail
def user_login_data(view_func):
    """自定义装饰器获取用户登录信息
    特点：装饰器会修改被装饰函数的__name__属性, 改成wrapper"""
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        # 具体的获取user_id,使用user_id获取用户信息
        user_id = session.get("user_id", None)
        user = None
        if user_id:
            try:
                # 查询用户信息
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        g.user = user
        # 调用被装饰的函数
        return view_func(*args, **kwargs)
    return wrapper

# 封装函数的形式获取用户登录信息
# def user_login_data():
#     user_id = session.get("user_id",None)
#     user = None
#     if user_id:
#         try:
#             # 查询用户信息
#             user = User.query.get(user_id)
#         except Exception as e:
#             current_app.logger.error(e)
#     return user