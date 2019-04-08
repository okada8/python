
from . import index_blu
from flask import render_template,g,abort
from flask import current_app,request,jsonify
from info.models import User,News,Category
from info.utils.response_code import RET
from info import constants
from info.utils.common import user_login_data

@index_blu.route('/new_list')
def news_list():
    """
    获取首页新闻参数
    :return:
    """
    #获取参数
    #新闻分类id
    cid=request.args.get("cid","1")
    page=request.args.get("page","1")
    per_page=request.args.get("per_page","10")
    #校验参数
    try:
        cid=int(cid)
        page=int(page)
        per_page=int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    filters=[]
    if cid !=1:
        filters.append(News.category_id==cid)
    #查询数据
    try:
        paginate=News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,per_page,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR,errmsg="数据查询错误")
    #取到当前页的数据
    news_list=paginate.items#模型对象列表
    total_page=paginate.pages
    current_page=paginate.page
    #将模型对象列表转成字典列表
    news_dict_li=[]
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())
    data={
        "total_page":total_page,
        "current_pade":current_page,
        "news_dict_li":news_dict_li,
    }
    return jsonify(error=RET.OK,errmsg="ok",data=data)



@index_blu.route('/')
@user_login_data
def index():
    user=g.user
    #右侧新闻排行逻辑
    news_list=[]
    try:
        news_list=News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    news_dict_li=[]
    #遍历对象列表
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    # 新闻分类数据
    categories = Category.query.all()
    category_li = []
    for category in categories:
        category_li.append(category.to_dict())


    data = {
        "user": user.to_dict() if user else None,
        "news_dict_li":news_dict_li,
        "category_li":category_li,

    }
    return render_template('news/index.html',data=data)


@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file("news/favicon.ico")