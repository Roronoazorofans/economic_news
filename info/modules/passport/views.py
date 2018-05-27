# coding=utf-8
import random, re, json
from flask import request, abort, current_app, make_response, jsonify
from info import constants
from info import response_code
from . import passport_blue
from info.utils.captcha.captcha import captcha
from info import redis_store
from info.libs.yuntongxun.sms import CCP


@passport_blue.route("/sms_code", methods=["POST"])
def sms_code():
    """发送短信验证码
    1. 接受参数(手机号，图片验证码，图片验证码编号)
    2. 校验参数(判断参数是否存在，手机号是否合法)
    3. 查询数据库中的验证码
    4. 对比客户端输入的验证码是否一致
    5. 如果对比成功，生成短信验证码数字
    6. 调用CCP单例类发送短信验证码的方法，发送短信
    7. 将短信验证码存储到服务器(将来注册时要判断短信验证码是否正确)
    8. 响应发送短信验证码的结果
    """
    json_str = request.data
    json_dict = json.loads(json_str.decode())
    mobile = json_dict.get("mobile")
    image_code_client = json_dict.get("image_code")
    image_code_id = json_dict.get("image_code_id")
    if not all([mobile, image_code_client, image_code_id]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
    if not re.match(r'^1[345678][0-9]{9}$', mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='⼿手机号格式错误')
    try:
        image_code_server = redis_store.get("ImageCode" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询图⽚片验证码失败')
    if not image_code_server:
        return jsonify(errno=response_code.RET.NODATA, errmsg='图⽚片验证码不不存在')
    if image_code_server != image_code_client:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='图⽚片验证码输⼊入有误')
    sms_code = '%06d' % random.randint(0,999999)
    result = CCP().send_template_sms(mobile, [sms_code, '5'],'1')
    if result != 0:
        return jsonify(errno=response_code.RET.THIRDERR, errmsg='发送短信验证码失败')
    try:
        redis_store.set("SMS:" +mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES )
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='存储短信验证码失败')
    return jsonify(errno=response_code.RET.OK, errmsg='发送短信验证码成功')






# @passport_blue.route("/image_code")
# def image_code():
#     """提供图片验证码"""
#     # 1. 获取imageCodeId
#     imageCodeId = request.args.get("imageCodeId")
#     # 2. 校验参数
#     if not imageCodeId:
#         abort(403)
#     # 3. 生成图片验证码
#     name,text,image = captcha.generate_captcha()
#     # 4. 保存图片验证码到redis数据库
#     try:
#         redis_store.set('ImageCode'+imageCodeId, text, constants.IMAGE_CODE_REDIS_EXPIRES)
#     except Exception as e:
#         current_app.logger.error(e)
#         abort(500)
#     # 5. 响应图片验证码
#     response = make_response(image)
#     response.headers['Content-Type'] = 'image/jpg'
#     return response

@passport_blue.route('/image_code')
def image_code():
    """提供图片验证码
    1.接受参数（图片验证码唯一标识uuid）
    2.校验参数（判断参数是否存在）
    3.生成图片验证码
    4.存储图片验证码
    5.将图片的类型指定为image/jpg
    6.响应图片验证码
    """
    # 1.接受参数（图片验证码唯一标识uuid）
    print('hello')
    imageCodeId = request.args.get('imageCodeId')

    # 2.校验参数（判断参数是否存在）
    if not imageCodeId:
        abort(403)

    # 3.生成图片验证码:text写入到redis,image响应到浏览器
    name,text,image = captcha.generate_captcha()

    # 4.存储图片验证码
    try:
        redis_store.set('ImageCode:'+imageCodeId, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)

    # 5.将图片的类型指定为image/jpg
    response = make_response(image)
    # 设置响应头信息
    response.headers['Content-Type'] = 'image/jpg'

    # 6.响应图片验证码
    return response