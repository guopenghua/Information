from . import passport_blue
from flask import request, jsonify, current_app, make_response
from info.utils.captcha.captcha import captcha
from info import redis_store, response_code, constants

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

    try:
        redis_store.set("imageCodeId" + imageCodeId, text)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DATAERR, errmsg="保存图片验证码失败")

    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"
    return response

