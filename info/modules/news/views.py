from . import news_blue
from info.utils.comment import user_login_data
from flask import render_template, g, current_app, jsonify
from info import response_code, constants, db
from info.models import News

@news_blue.route("/detail/<int:news_id>")
@user_login_data
def news_detail(news_id):
    """新闻详情页"""
    # 1. 用户是否登录
    user = g.user

    # 2. 点击排行
    news_clicks = []
    try:
        news_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    # 3. 获取参数
    news_id = news_id

    # 4. 校验参数
    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg="参数错误")

    # 5. 获取新闻内容
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg="获取新闻数据失败")

    if not news:
        return jsonify(errno=response_code.RET.NODATA, errmsg="查询的新闻不存在")

    # 6. 新闻点击量增加
    news.clicks += 1
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=response_code.RET.DBERR, errmsg="点击量+1失败")

    # 7. 是否收藏
    is_collected = False
    if user:
        if news_id in user.collection_news:
            is_collected = True

    context = {

        "user": user,
        "news": news.to_dict(),
        "news_clicks": news_clicks,
        "is_collected": is_collected
    }

    #  响应页面
    return render_template("news/detail.html", context=context)