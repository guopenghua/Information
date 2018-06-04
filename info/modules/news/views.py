from . import news_blue
from info.utils.comment import user_login_data
from flask import render_template

@news_blue.route("/detail/<int:news_id>")
@user_login_data
def news_detail(news_id):
    """新闻详情页"""
    # 1. 用户是否登录
    # 2. 获取参数
    # 3. 校验参数
    # 4. 响应页面
    return render_template("news/detail.html")