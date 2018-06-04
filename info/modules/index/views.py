from . import index_blue
from flask import render_template, current_app, request, session, jsonify, make_response
from info.models import User, News
from info import constants, response_code


@index_blue.route("/news_list")
def index_news_list():
    """主页面新闻展示"""
    # 1. 接收参数,进行校验
    cid = request.args.get("cid", "1")
    page = request.args.get("page", "1")
    per_page = request.args.get("per_page", "10")

    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg="参数错误")

    if cid == 1:
        paginate = News.query.order_by(News.create_time.desc()).paginate(page, per_page, False)
    else:
        paginate = News.query.filter(News.category_id == cid).order_by(News.create_time.desc()).paginate(page, per_page, False)

    # 取出当前页所有的模型对象
    news_list = paginate.items
    total_page = paginate.pages
    current_page = paginate.page

    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())
    context = {
        "news_dict_list": news_dict_list,
        "total_page": total_page,
        "current_page": current_page
    }

    return jsonify(errno=response_code.RET.OK, errmsg="OK", context=context)

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

    # 2. 点击排行
    news_clicks = []
    try:
        news_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    context = {
        "user": user,
        "news_clicks": news_clicks
    }

    return render_template("news/index.html", context=context)


@index_blue.route("/favicon.ico")
def favicon():
    return current_app.send_static_file("news/favicon.ico")
