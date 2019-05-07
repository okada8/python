from info.modules.news import news_blu
from flask import render_template, g, abort
from flask import current_app, request, jsonify
from info.models import Comment, News, CommentLike, User
from info import constants, db
from info.utils.common import user_login_data
from info.utils.response_code import RET


@news_blu.route('/followed_user', methods=["POST"])
@user_login_data
def followed_user():
    """关注或者取消关注"""
    # 取参数
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="未登录")
    user_id = request.json.get("user_id")
    action = request.json.get("action")
    if not all([user_id, action]):
        return jsonify(error=RET.PARAMERR, errmsg="参数错误")
    if action not in ["follow", "unfollow"]:
        return jsonify(error=RET.PARAMERR, errmsg="参数错误")
    try:
        other = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.PARAMERR, errmsg="数据查询错误")
    if not other:
        return jsonify(error=RET.NODATA, errmsg="未查询到数据")
    if action == "follow":
        if other not in user.followed and other.id != user.id:
            user.followed.append(other)
        else:
            return jsonify(error=RET.DATAEXIST, errmsg="当前用户已被关注")
    else:
        if other in user.followed:
            user.followed.remove(other)
        else:
            return jsonify(error=RET.DATAEXIST, errmsg="当前用户未被关注")
    return jsonify(errno=RET.OK, errmsg="操作成功")


@news_blu.route('/comment_like', methods=["POST"])
@user_login_data
def comment_like():
    """
    点赞和取消点赞
    :return:
    """
    user = g.user
    current_app.logger.error(user.to_dict())
    if not user:
        return jsonify(error=RET.SESSIONERR, errmsg="用户未登录")
        # 取请求参数
    # news_id = request.json.get("news_id")
    comment_id = request.json.get("comment_id")
    action = request.json.get("action")
    current_app.logger.error(request.json)
    if not all([comment_id, action]):
        return jsonify(error=RET.PARAMERR, errmsg="参数错误")
    if action not in ["add", "remove"]:
        return jsonify(error=RET.PARAMERR, errmsg="参数错误")
    try:
        comments_id = int(comment_id)
        # news_id=int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.PARAMERR, errmsg="参数错误")
    try:
        comment = Comment.query.get(comments_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="数据查询错误")
    if not comment:
        return jsonify(error=RET.NODATA, errmsg="评论不存在")

    if action == "add":
        commentss_like = CommentLike.query.filter(CommentLike.comment_id == comments_id,
                                                  CommentLike.user_id == user.id).first()
        if not commentss_like:
            commentss_like = CommentLike()
            commentss_like.comment_id = comments_id
            commentss_like.user_id = g.user.id
            db.session.add(commentss_like)
            comment.like_count += 1
            current_app.logger.error([commentss_like.comment_id])
    else:
        comment_likess = CommentLike.query.filter(CommentLike.user_id == user.id,
                                                  CommentLike.comment_id == comment.id).first()
        if comment_likess:
            db.session.delete(comment_likess)
            comment.like_count -= 1
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库操作失败")
    return jsonify(errno=RET.OK, errmsg="OK")


@news_blu.route('/news_comment', methods=["POST"])
@user_login_data
def comment_news():
    """
    评论新闻或者回复评论
    :return:
    """
    user = g.user
    if not user:
        return jsonify(error=RET.SESSIONERR, errmsg="用户未登录")

    # 取请求参数
    news_id = request.json.get("news_id")
    comment_count = request.json.get("comment")
    parent_id = request.json.get("parent_id")
    # 参数判断
    if not all([news_id, comment_count]):
        current_app.logger.error([request.json])
        return jsonify(error=RET.PARAMERR, errmsg="参数错误")
    try:
        news_id = int(news_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.PARAMERR, errmsg="参数错误")
    # 查询新闻数据
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
    if not news:
        abort(404)

    # 初始化评论模型添加到数据库
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news_id
    comment.content = comment_count
    if parent_id:
        comment.parent_id = parent_id
    # 添加到数据库
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

    return jsonify(errno=RET.OK, errmsg="OK", data=comment.to_dict())


@news_blu.route('/news_collect', methods=['POST'])
@user_login_data
def news_collect():
    """
    收藏新闻和取消收藏
    :return:
    """
    user = g.user
    if not user:
        return jsonify(error=RET.SESSIONERR, errmsg="用户未登录")
    news_id = request.json.get("news_id")
    action = request.json.get("action")
    if not all([news_id, action]):
        return jsonify(error=RET.PARAMERR, errmsg="参数错误")
    if action not in ["collect", "cancel_collect"]:
        return jsonify(error=RET.PARAMERR, errmsg="参数错误")
    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.PARAMERR, errmsg="参数错误")
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="数据查询错误")
    if not news:
        return jsonify(error=RET.NODATA, errmsg="未查询到数据")
    if action == "cancel_collect":
        if news in user.collection_news:
            user.collection_news.remove(news)
    else:
        if news not in user.collection_news:
            user.collection_news.append(news)
    return jsonify(error=RET.OK, errmsg="操作成功")


@news_blu.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    """
    新闻详情
    :param news_id:
    :return:
    """
    # 如果用户已经登录 将用户登录数据传入模板
    user = g.user
    # 右侧新闻排行逻辑
    news_list = []
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    news_dict_li = []
    # 遍历对象列表
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    # 查询新闻数据
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
    if not news:
        abort(404)
    # 更新新闻点击次数
    news.clicks += 1
    is_clicks = False
    if user:
        if news in user.collection_news:
            is_clicks = True

    # 查询评论数据
    comments = []
    try:
        # 查出当前新闻的所有评论
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
    comment_like_ids = []
    if g.user:
        try:
            # 查出当前新闻的所有评论，取到所有评论id【1，2，3，4，5】
            comment_ids = [comment.id for comment in comments]
            # 查询当前哪些评论被当前用户点过赞返回的是评论对象
            comment_likes = CommentLike.query.filter(CommentLike.comment_id.in_(comment_ids),
                                                     CommentLike.user_id == user.id).all()
            # 取到被点赞的评论id列表【3,5】
            comment_like_ids = [comment_like.comment_id for comment_like in comment_likes]
        except Exception as e:
            current_app.logger.error(e)

    comment_dic_li = []
    for comment in comments:
        comment_dic = comment.to_dict()
        comment_dic["is_like"] = False
        # 判断当前遍历的评论id是否被点过赞
        if comment.id in comment_like_ids:
            comment_dic["is_like"] = True
        comment_dic_li.append(comment_dic)

    is_followed = False
    if news.user and user:
        if news.user in user.followed:
            is_followed = True

    data = {
        "user": user.to_dict() if user else None,
        "news_dict_li": news_dict_li,
        "news": news.to_dict(),
        "is_collected": is_clicks,
        "comments": comment_dic_li,
        "is_followed": is_followed
    }

    return render_template("news/detail.html", data=data)
