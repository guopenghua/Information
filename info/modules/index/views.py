from . import index_blue
from flask import render_template, current_app, jsonify, session
from info.models import User

@index_blue.route("/")
def index():
    """主页"""
    # 1. 右上角用户登录状态
    user_id = session.get("user_id", None)
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    context = {
        "user": user
    }

    return render_template("news/index.html", context=context)


@index_blue.route("/favicon.ico")
def favicon():
    return current_app.send_static_file("news/favicon.ico")
