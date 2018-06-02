from . import passport_blue
from flask import request, jsonify, current_app, make_response, session
from info.utils.captcha.captcha import captcha
from info import redis_store, response_code, constants, db
import re, random
from info.lib.yuntongxun.sms import CCP
from info.models import User
import datetime

@passport_blue.route("/logout")
def logout():
    """登出"""
    try:
        session.pop("user_id")
        session.pop("nick_name")
        session.pop("mobile")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg="取消登录状态保持失败")
    return jsonify(errno=response_code.RET.OK, errmsg="退出登录成功")


@passport_blue.route("/login", methods=["POST"])
def login():
    """登录"""
    # 1. 获取参数(手机号 密码)
    mobile = request.json.get("mobile")
    password = request.json.get("password")

    # 2. 校验参数
    if not all([mobile, password]):
        return jsonify(errno=response_code.RET.DATAERR, errmsg="缺少参数")

    if not re.match(r"^1[345678][0-9]{9}$", mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg="手机号格式有误")

    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg="查询用户数据失败")

    if not user:
        return jsonify(errno=response_code.RET.NODATA, errmsg="用户或密码输入有误")

    if user.password_hash != password:
        return jsonify(errno=response_code.RET.DATAERR, errmsg="用户或密码输入有误")

    # 3. 状态保持
    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile

    # 4. 响应
    return jsonify(errno=response_code.RET.OK, errmsg="登录成功")

@passport_blue.route("/register", methods=["POST"])
def register():
    """注册"""
    # 1. 接收参数
    mobile = request.json.get("mobile")
    sms_code_client = request.json.get("smscode")
    password = request.json.get("password")

    # 2. 校验参数
    if not all([mobile, sms_code_client, password]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg="参数不全")

    if not re.match(r"^1[345678][0-9]{9}$", mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg="手机号格式有误")

    try:
        sms_code_server = redis_store.get("sms_code" + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg="读取短信验证码失败")

    if not sms_code_server:
        return jsonify(errno=response_code.RET.NODATA, errmsg="短信验证码不存在")

    if sms_code_server != sms_code_client:
        return jsonify(errno=response_code.RET.DATAERR, errmsg="短信验证码有误")

    # 3. 校验正确, 保存密码
    user = User()
    user.mobile = mobile
    user.password_hash = password
    user.nick_name = mobile
    user.last_login = datetime.datetime.now()

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg="保存注册用户信息失败")

    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile

    # 4. 返回响应
    return jsonify(errno=response_code.RET.OK, errmsg="注册成功")


@passport_blue.route("/sms_code", methods=["POST"])
def sms_code():
    """发送短信验证码"""
    # 1. 接收参数(手机号 图片验证码)
    mobile = request.json.get("mobile")
    image_code_client = request.json.get("image_code")
    image_code_id = request.json.get("image_code_id")

    # 2. 校验参数
    if not all([mobile, image_code_client, image_code_id]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg="参数不全")

    if not re.match(r"^1[345678][0-9]{9}$", mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg="手机号格式有误")

    try:
        image_code_server = redis_store.get("imageCodeId" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg="读取图片验证码失败")

    if not image_code_server:
        return jsonify(errno=response_code.RET.NODATA, errmsg="图片验证码不存在")

    if not image_code_server.lower() == image_code_client.lower():
        return jsonify(errno=response_code.RET.DATAERR, errmsg="图片验证码不正确")

    # 3. 参数正确,生成短信验证码
    result = random.randint(0, 999999)
    sms_code = "%06d" % result
    current_app.logger.error(sms_code)

    # 4. 保存短信验证码
    try:
        redis_store.set("sms_code" + mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg="保存短信验证码失败")


    # result = CCP().send_template_sms(mobile, [sms_code, 5], 1)
    # if result != 0:
    #     return jsonify(errno=response_code.RET.THIRDERR, errmsg="发送短信验证码失败")

    # 5. 响应
    return jsonify(errno=response_code.RET.OK, errmsg="发送短信验证码成功")


@passport_blue.route("/image_code")
def get_image_code():
    """生成图片验证码
    1. 接收参数 imageCodeId
    2. 调用方法 生成图片验证码
    3. 保存数据
    4. 响应数据
    """
    imageCodeId = request.args.get("imageCodeId")
    name, text, image = captcha.generate_captcha()
    current_app.logger.error(text)
    try:
        redis_store.set("imageCodeId" + imageCodeId, text)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DATAERR, errmsg="保存图片验证码失败")
    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"
    return response

