from . import profile_blu
from flask import render_template, current_app
from flask import g, redirect, request, jsonify, abort
from info.utils.common import user_login_data
from info.utils.response_code import RET
from info.utils.image_storage import storge
from info import constants, db
from info.models import Category, News, User


@profile_blu.route('/other_new_list')
def other_new_list():
    """
    返回指定用户发布的新闻
    :return:
    """
    # 先拿到指定用户的id
    other_id = request.args.get("user_id")
    current_app.logger.error(other_id)
    page = request.args.get("p", 1)
    current_app.logger.error(page)

    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.PARAMERR, errmsg='参数错误')
    # 去当前用户所发布的新闻
    try:
        other = User.query.get(other_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.PARAMERR, errmsg='数据查询错误')
    if not other:
        return jsonify(error=RET.NODATA, errmsg='当前用户不存在')
    # 去用户的新闻
    try:
        paginat = other.news_list.paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        # 4.获取分页对象属性,总页数,当前页,当前页对象
        total_page = paginat.pages
        current_page = paginat.page
        news_li = paginat.items
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.PARAMERR, errmsg='数据查询错误')
    news_dic_li = []
    for news in news_li:
        news_dic_li.append(news.to_basic_dict())
    current_app.logger.error(news_dic_li)
    if not news_dic_li:
        return jsonify(error=RET.OK, errmsg='该用户未发布新闻', )

    data = {
        "total_page": total_page,
        "current_page": current_page,
        "collection": news_dic_li
    }
    return jsonify(error=RET.OK, errmsg='OK', data=data)


@profile_blu.route('/other_info')
@user_login_data
def other_info():
    # 取出其他人用户信息id
    other_id = request.args.get("user_id")
    if not other_id:
        abort(404)
        # return render_template('news/other.html', errmsg="参数错误")
    # 根据id查询出其他用户信息
    try:
        other_id = int(other_id)
        others = User.query.get(other_id)
    except Exception as e:
        current_app.logger.error(e)
        return render_template('news/other.html', errmsg="数据查询失败")
    if not others:
        abort(404)

    is_followed = False
    if others and g.user.followed:
        if others in g.user.followed:
            is_followed = True

    data = {"user": g.user.to_dict() if g.user else None,
            "other": others.to_dict(),
            "is_followed ": is_followed
            }
    return render_template('news/other.html', data=data)


@profile_blu.route('/user_follow')
@user_login_data
def user_follow():
    user = g.user
    # 获取页数
    page = request.args.get("p", 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    follows = []
    current_page = 1
    total_page = 1

    # 3.分页查询数据
    try:
        paginate = g.user.followed.paginate(page, 4, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户失败")

    # 4.获取分页对象属性,总页数,当前页,当前页对象
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5.对象列表转字典列表
    user_list = []
    for item in items:
        user_list.append(item.to_dict())

    # 6.拼接数据返回页面渲染
    data = {
        "total_page": totalPage,
        "current_page": currentPage,
        "user_list": user_list
    }
    return render_template('news/user_follow.html', data=data)


@profile_blu.route('/news_list')
@user_login_data
def user_news_list():
    page = request.args.get("p", 1)
    news_list = []
    current_page = 1
    total_page = 1
    try:
        paginate = News.query.filter(News.user_id == g.user.id).paginate(page, constants.USER_COLLECTION_MAX_NEWS,
                                                                         False)
        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)
    news_dic_list = []
    for news in news_list:
        news_dic_list.append(news.to_basic_dict())
    data = {"news_list": news_dic_list,
            "total_page": total_page,
            "current_page": current_page
            }

    return render_template('news/user_news_list.html', data=data)


@profile_blu.route('/news_release', methods=["GET", "POST"])
@user_login_data
def news_release():
    # 若果是获取数据，请求方式就为get
    if request.method == "GET":
        """
        发布新闻
        :return:
        """
        # 加载新闻数据
        categories = []
        try:
            # 从数据库拿出所有新闻类型字段
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
        categories_li = []
        # 拿出每一个新闻字段
        for categor in categories:
            categories_li.append(categor.to_dict())
        # 去除索引为0的那个新闻类型字段
        categories_li.pop(0)
        data = {"categories": categories_li}
        return render_template('news/user_news_release.html', data=data)
    # 要发布新闻，先获取数据，请求数据类型为post
    # 新闻标题
    title = request.form.get("title")
    # 新闻来源
    source = "个人发布"
    # 新闻摘要
    digest = request.form.get("digest")
    # 新闻内容
    content = request.form.get("content")
    # 新闻索引图片,将图片上传到os对象存储
    try:
        index_image = request.files.get("index_image").read()
        # 保存新闻到os对象存除
        key = storge(index_image)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.PARAMERR, errmsg='请上传新闻图片')
    # 新闻分类id
    category_id = request.form.get("category_id")
    # 判断和校验参数
    if not all([title, digest, content, index_image, category_id]):
        return jsonify(error=RET.PARAMERR, errmsg='参数错误')
    try:
        category_id = int(category_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.PARAMERR, errmsg='参数错误')
    # 初始化新闻模型
    news = News()
    news.title = title
    news.digest = digest
    news.source = source
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
    news.category_id = category_id
    news.user_id = g.user.id
    # 审核状态
    news.status = 1
    try:
        # 将模型添加到数据库
        db.session.add(news)
        # 数据保存提交
        db.session.commit()
    except Exception as e:
        # 如果有报错，数据回滚
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg='数据保存失败')
    return jsonify(errno=RET.OK, errmsg='OK')


@profile_blu.route('/collection')
@user_login_data
def user_collection():
    # 获取页数
    page = request.args.get("p", 1)
    # 判断参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    # 获取用户收藏新闻
    news_dic_li = []
    news_list = []
    total_page = 1
    current = 1
    try:
        paginate = g.user.collection_news.paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        current = paginate.page
        total_page = paginate.pages
        news_list = paginate.items
    except Exception as e:
        current_app.logger.error(e)

    for news in news_list:
        news_dic_li.append(news.to_basic_dict())
    data = {
        "total_page": total_page,
        "current_page": current,
        "collection": news_dic_li
    }

    return render_template('news/user_collection.html', data=data)


@profile_blu.route('/pass_info', methods=["GET", "POST"])
@user_login_data
def pass_info():
    # 加载用户的当前昵称和个人签名，是get方式
    if request.method == "GET":
        data = {"user": g.user.to_dict()}
        return render_template('news/user_pass_info.html')
    # 获取参数
    news_password = request.json.get("new_password")
    old_password = request.json.get("old_password")
    if not all([news_password, old_password]):
        return jsonify(error=RET.PARAMERR, errmsg='参数错误')
    # 校验参数,判断旧密码
    if not g.user.check_passowrd(old_password):
        return jsonify(error=RET.PWDERR, errmsg='原密码错误')
    # 设置新密码
    g.user.password = news_password
    return jsonify(errno=RET.OK, errmsg='保存成功')


@profile_blu.route('/pic_info', methods=["GET", "POST"])
@user_login_data
def pic_info():
    # 加载用户的当前昵称和个人签名，是get方式
    if request.method == "GET":
        data = {"user": g.user.to_dict()}
        return render_template('news/user_pic_info.html', data=data)
    # 拿到上传图片的文件对象
    try:
        avatr = request.files.get("avatar_url").read()

    except Exception as e:
        current_app.logger.error(request.files.get("avatar_url"))
        current_app.logger.error(e)
        return jsonify(error=RET.PARAMERR, errmsg='参数错误')
    # 将文件上传到第三方云存储
    try:
        key = storge(avatr)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.THIRDERR, errmsg='上传头像错误')
    # 把头像地址保存到数据库
    g.user.avatar_url = key
    return jsonify(errno=RET.OK, errmsg='OK', data={"avatar_url": constants.QINIU_DOMIN_PREFIX + key})


@profile_blu.route('/base_info', methods=["GET", "POST"])
@user_login_data
def base_info():
    # 加载用户的当前昵称和个人签名，是get方式
    if request.method == "GET":
        data = {"user": g.user.to_dict()}
        return render_template('news/user_base_info.html', data=data)
    # 要修改用户数据，需要接受参数
    current_app.logger.error(request.json)
    nick_name = request.json.get("nick_name")
    signature = request.json.get("signature")
    gender = request.json.get("gender")

    # 判断参数
    if not all([nick_name, signature, gender]):
        return jsonify(error=RET.PARAMERR, errmsg='参数错误')
    if gender not in ["MAN", "WOMAN"]:
        return jsonify(error=RET.PARAMERR, errmsg='参数错误')
    # 根据用户模型来修改,
    g.user.signature = signature
    g.user.gender = gender
    g.user.nick_name = nick_name

    return jsonify(errno=RET.OK, errmsg='OK')


@profile_blu.route('/info')
@user_login_data
def user_info():
    user = g.user
    # 如果没有登录直接重定向到首页
    if not user:
        return redirect("/")

    data = {"user": user.to_dict()}
    return render_template('news/user.html', data=data)
