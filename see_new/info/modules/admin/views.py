from flask import render_template, request, current_app
from flask import session, redirect, url_for, g, jsonify, abort
from info.modules.admin import admin_blu
from info.models import User, News, Category
from info.utils.common import user_login_data
from datetime import datetime, timedelta
from info import constants, db
from info.utils.response_code import RET
from info.utils.image_storage import storge
import time


@admin_blu.route('/news_type', methods=["POST", "GET"])
def news_type():
    if request.method == "GET":
        try:
            categories = Category.query.all()

        except Exception as e:
            current_app.logger.error(e)
            return render_template('admin/news_type.html', errmsg="数据查询错误")
        category_list_dic = []
        for category in categories:
            cate_dict = category.to_dict()
            category_list_dic.append(cate_dict)

        category_list_dic.pop(0)
        data = {"categories": category_list_dic}
        return render_template('admin/news_type.html', data=data)
    # 编辑新闻分类
    # 取参数
    c_name = request.json.get("name")
    cid = request.json.get("id")
    # 必须要有分类名字
    if not c_name:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 如果有分类id，说明是修改分类名，不用add到数据库
    if cid:
        try:
            cid = int(cid)
            # 拿到对应分类
            category = Category.query.get(cid)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        if not category:
            return jsonify(errno=RET.PARAMERR, errmsg="未查询到分类数据")
        # 更改分类名，自动添加到数据库
        category.name = c_name
    # 增加分类
    else:
        category = Category()
        category.name = c_name
        db.session.add(category)
    return jsonify(errno=RET.OK, errmsg="OK")


@admin_blu.route('/news_edit_detail', methods=["GET", "POST"])
def news_edit_detail():
    if request.method == "GET":
        # 查询点击新闻相关数据
        news_id = request.args.get("news_id")
        if not news_id:
            abort(404)
        try:
            news_id = int(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return render_template('admin/news_edit_detail.html', errmsg="参数错误")
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return render_template('admin/news_edit_detail.html', errmsg="数据查询错误")
        if not news:
            return render_template('admin/news_edit_detail.html', errmsg="没有相关数据")

        try:
            categories = Category.query.all()

        except Exception as e:
            current_app.logger.error(e)
            return render_template('admin/news_edit_detail.html', errmsg="数据查询错误")
        category_list_dic = []
        for category in categories:
            cate_dict = category.to_dict()
            if category.id == news.category_id:
                cate_dict["is_selected"] = True
            category_list_dic.append(cate_dict)
        category_list_dic.pop(0)
        data = {"news": news.to_dict(), "categories": category_list_dic}

        return render_template('admin/news_edit_detail.html', data=data)
    # 取到被提交的数据
    news_id = request.form.get("news_id")
    title = request.form.get("title")
    digest = request.form.get("digest")
    content = request.form.get("content")
    index_image = request.files.get("index_image")
    category_id = request.form.get("category_id")
    if not all([title, digest, content, category_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到新闻数据")

    # 4.上传图片
    if index_image:
        try:
            key = storge(index_image.read())
            news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg="七牛云上传异常")
    # 数据库保存

    news.title = title
    news.digest = digest
    news.content = content
    news.category_id = category_id

    return jsonify(errno=RET.OK, errmsg="OK")


# 新闻编辑
@admin_blu.route('/news_edit')
def news_edit():
    page = request.args.get("p", 1)
    keywords = request.args.get("keywords", None)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    news_list = []
    current_page = 1
    total_page = 1

    filters = [News.status == 0]
    if keywords:
        filters.append(News.title.contains(keywords))
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,
                                                                                          constants.ADMIN_NEWS_PAGE_MAX_COUNT,
                                                                                          False)
        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())
    data = {
        "total_page": total_page,
        "current_page": current_page,
        "news_list": news_dict_list
    }

    return render_template('admin/news_edit.html', data=data)


# 新闻审核
@admin_blu.route('/news_review_action', methods=["POST"])
def news_review_action():
    news_id = request.json.get("news_id")
    action = request.json.get("action")
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ("accept", "reject"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到数据")
    if action == "accept":
        news.status = 0
    else:
        requests = request.json.get("reason")
        if not requests:
            return jsonify(errno=RET.PARAMERR, errmsg="请输入拒绝原因")

        news.status = -1
        news.reason = requests
    return jsonify(erron=RET.OK, errmsg="OK")


@admin_blu.route('/news_review_detail/<int:news_id>')
def news_review_detail(news_id):
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
    if not news:
        return render_template("admin/news_review_detail.html", data={"errmsg": "未查询到此新闻"})

    data = {
        "news": news.to_dict()
    }

    return render_template("admin/news_review_detail.html", data=data)


@admin_blu.route('/news_review')
def news_review():
    page = request.args.get("p", 1)
    keywords = request.args.get("keywords", None)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    news_list = []
    current_page = 1
    total_page = 1

    filters = [News.status != 0]
    if keywords:
        filters.append(News.title.contains(keywords))
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,
                                                                                          constants.ADMIN_NEWS_PAGE_MAX_COUNT,
                                                                                          False)
        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_review_dict())
    data = {
        "total_page": total_page,
        "current_page": current_page,
        "news_list": news_dict_list
    }

    return render_template('admin/news_review.html', data=data)


@admin_blu.route('/user_list')
def user_list():
    # 用户列表
    page = request.args.get('page')
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    users = []
    current_page = 1
    total_page = 1
    try:
        paginate = User.query.filter(User.is_admin == False).paginate(page, constants.ADMIN_USER_PAGE_MAX_COUNT)
        users = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)
    user_dic_li = []
    for user in users:
        user_dic_li.append(user.to_admin_dict())
    data = {
        "users": user_dic_li,
        "current_page": current_page,
        "total_page": total_page
    }
    return render_template('admin/user_list.html', data=data)


@admin_blu.route('/user_count')
def user_count():
    """
     新增人数，折线图
    :return:
    """
    total_count = 0
    mon_count = 0
    day_count = 0
    t = time.localtime()
    # 月初
    data_time = datetime.strptime(("%d-%02d-01" % (t.tm_year, t.tm_mon)), "%Y-%m-%d")
    # 今天
    day_time = datetime.strptime(("%d-%02d-%02d" % (t.tm_year, t.tm_mon, t.tm_mday)), "%Y-%m-%d")
    try:
        total_count = User.query.filter(User.is_admin == False).count()
        mon_count = User.query.filter(User.is_admin == False, User.create_time > data_time).count()
        day_count = User.query.filter(User.is_admin == False, User.create_time > day_time).count()
        current_app.logger.error([day_time, data_time])
    except Exception as e:
        current_app.logger.error(e)

    # 折线图
    # 以天为时间
    active = []
    # 人数
    active_count = []
    # 今天0点0分
    begin_day = datetime.strptime(("%d-%02d-%02d" % (t.tm_year, t.tm_mon, t.tm_mday)), "%Y-%m-%d")
    for i in range(0, 31):
        # 某一天的0点0分
        begin_data = begin_day - timedelta(days=i)
        # 下一天的0点0分
        end_data = begin_day - timedelta(days=(i - 1))
        count = User.query.filter(User.is_admin == False, User.last_login >= begin_data,
                                  User.last_login < end_data).count()
        active_count.append(count)
        active.append(begin_data.strftime("%Y-%m-%d"))
    # 反转
    active.reverse()
    active_count.reverse()
    data = {
        "total_count": total_count,
        "mon_count": mon_count,
        "day_count": day_count,
        "active": active,
        "active_count": active_count
    }

    return render_template('admin/user_count.html', data=data)


@admin_blu.route('/index')
@user_login_data
def index():
    """
    管理员用户界面
    :return:
    """
    user = g.user
    data = {"user": user.to_dict()}
    return render_template('admin/index.html', data=data)


@admin_blu.route('/login', methods=["GET", "POST"])
def login():
    """
    后台管理员登录
    :return:
    """
    if request.method == "GET":
        # 先判断是否有登录
        user_id = session.get("user_id", None)
        is_admin = session.get("is_admin", False)
        if user_id and is_admin:
            # 如果管理员有登录直接跳到主页
            return redirect(url_for('admin.index'))
        return render_template('admin/login.html')
    # 取到登录参数
    username = request.form.get("username")
    password = request.form.get("password")
    # 判断参数
    if not all([username, password]):
        return render_template('admin/login.html', errmsg="参数错误")
    # 查询当前用户
    try:
        user = User.query.filter(User.nick_name == username, User.is_admin == True).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/login.html', errmsg="用户信息查询失败")
    if not user:
        return render_template('admin/login.html', errmsg="用户不存在")
    # 校验密码
    if not user.check_passowrd(password):
        return render_template('admin/login.html', errmsg="密码错误")
    # 保存用状态
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name
    session["is_admin"] = user.is_admin
    # 跳转
    return redirect(url_for('admin.index'))
