from flask import render_template,request,current_app
from flask import session,redirect,url_for,g
from info.modules.admin import admin_blu
from info.models import User
from info.utils.common import user_login_data


@admin_blu.route('/index')
@user_login_data
def index():
    """
    管理员用户界面
    :return:
    """
    user=g.user


    data={"user":user.to_dict()}






    return render_template('admin/index.html',data=data)




@admin_blu.route('/login',methods=["GET","POST"])
def login():
    """
    后台管理员登录
    :return:
    """
    if request.method == "GET":
        #先判断是否有登录
        user_id=session.get("user_id",None)
        is_admin=session.get("is_admin",False)
        if user_id and is_admin:
            #如果管理员有登录直接跳到主页
            return redirect(url_for('admin.index'))
        return render_template('admin/login.html')
    #取到登录参数
    username=request.form.get("username")
    password=request.form.get("password")
    #判断参数
    if not all([username,password]):
        return render_template('admin/login.html',errmsg="参数错误")
    #查询当前用户
    try:
        user=User.query.filter(User.nick_name==username,User.is_admin==True).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/login.html', errmsg="用户信息查询失败")
    if not user:
        return render_template('admin/login.html', errmsg="用户不存在")
    #校验密码
    if not user.check_passowrd(password):
        return render_template('admin/login.html', errmsg="密码错误")
    # 保存用状态
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name
    session["is_admin"]=user.is_admin
    #跳转
    return redirect(url_for('admin.index'))