# coding=utf-8
from . import passport_blue


@passport_blue.route("/sms_code", methods=["GET"])
def get_image_code():
    """提供图片验证码"""
    #