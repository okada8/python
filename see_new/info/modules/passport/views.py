from . import passport_blu
from flask import request,make_response
from flask import abort,jsonify,session
from info.utils.captcha.captcha import captcha
from info import redis_store,constants,models,db
from flask import current_app
from info.utils.response_code import RET
from info.libs.yuntongxun.sms import CCP
from datetime import datetime
import re,random

#退出登录
@passport_blu.route('/logout')
def logout():
    """
    退出登录就是清除缓存
    """
    session.pop('user_id',None)
    session.pop('mobile', None)
    session.pop('nick_name', None)
    session.pop('is_admin', None)
    return jsonify(errno=RET.OK, errmsg="退出成功")

#登录逻辑
@passport_blu.route('/login',methods=['POST'])
def login():
    """
    1.获取参数
    2.校验参数
    3.校验密码是否正确
    4.保存用户等状态
    5.响应
    :return:
    """
    #获取参数
    params_dic=request.json
    current_app.logger.error(params_dic)
    mobile=params_dic.get('mobile')
    password=params_dic.get('password')
    current_app.logger.error(type(password))
    #校验参数
    if not all([mobile,password]):
        return jsonify(error=RET.PARAMERR,errmsg='参数错误')
    # 效验手机号码是否正确
    if not re.match('1[35678]\\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号码是否正确")
    #校验用户是否存在
    try:
        user=models.User.query.filter(models.User.mobile==mobile).first()
        current_app.logger.error(type(user))
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR,errmsg="数据查询错误")
    #判断用户是否存在
    if not user:
        return jsonify(error=RET.NODATA, errmsg="用户不存在")
    #校验密码
    if not user.check_passowrd(password):
        return jsonify(error=RET.PWDERR, errmsg="用户名或密码错误")
    #保存用状态
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name
    #记录用户最后一次登录时间并且保存的数据库，如果
    #配置了数据库自动保存，只需要更改模型，就可以自动加到数据库
    user.last_login=datetime.now()
    # 如果配置了SQLALCHEMY_COMMIT_ON_TEARDOWN=True，就可以忽略
    # try:
    #     #保存数据
    #     db.session.commit()
    # except Exception as e:
    #     db.session.rollback()
    #     current_app.logger.error(e)
    # 响应
    return jsonify(errno=RET.OK, errmsg="用户登录成功")


#注册逻辑
@passport_blu.route('/register',methods=["POST"])
def register():
    """
    1.获取参数
    2.校验参数
    3.取到服务器验证码
    4.比对验证码
    5.成功创建user模型 添加数据库
    6.返回值
    :return:
    """
    params_dict = request.json
    current_app.logger.error(params_dict)
    mobile = params_dict["mobile"]
    smscode = params_dict["smscode"]
    passwprd = params_dict["password"]

    #校验参数
    if not all([mobile,smscode,passwprd]):
        return jsonify(erron=RET.PARAMERR,errmsg='参数为空')
    #效验手机号码是否正确
    if not re.match('1[35678]\\d{9}',mobile):
        return jsonify(errno=RET.PARAMERR,errmsg="手机号码是否正确")
    #取到验证码
    try:
        real_sms_code=redis_store.get("SMS_"+mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据查询失败")
    if not real_sms_code:
        return jsonify(errno=RET.NODATA,errmsg="验证码已过期")
    #校验验证码
    if real_sms_code !=smscode:
        return jsonify(errno=RET.DBERR, errmsg="验证码输入错误")
    #生成新的用户
    user=models.User()
    user.mobile=mobile
    user.nick_name=mobile
    user.last_login=datetime.now()
    user.password=passwprd

    #添加到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    #往sesson中添加数据表示已经登录
    session["user_id"]=user.id
    session["mobile"]=user.mobile
    session["nick_name"]=user.nick_name

    #返回
    return jsonify(errno=RET.OK, errmsg="用户注册成功")


#短信验证码
@passport_blu.route('/sms_code',methods=["POST"])
def send_sms_code():
    """
    发送短信,获取图片验证码编号，手机号码，图片验证码内容
    :return:
    """
    #获取用户输入的手机号，图片验证码，图片编号
    # return jsonify(errno=RET.OK, errmsg="发送短信成功")
    params_dict=request.json

    mobile=params_dict["mobile"]
    image_code=params_dict["image_code"]
    image_code_id=params_dict["image_code_id"]
    #效验#参数是否有值
    if not all([mobile,image_code,image_code_id]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数有误")
    #效验手机号码是否正确
    if not re.match('1[35678]\\d{9}',mobile):
        return jsonify(errno=RET.PARAMERR,errmsg="手机号码是否正确")
    #从redis取出手机号
    try:
        real_image_code=redis_store.get("ImageCodeId_%s"% image_code_id)
        current_app.logger.debug("ImageCodeId_"+ image_code_id)
        current_app.logger.debug(real_image_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")
    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码已过期")
    #对比验证码
    if real_image_code.upper() != image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")
    #生成短信验证码,保证数字为6位，不够用0补上
    sms_code_str="%06d"%random.randint(0,999999)
    current_app.logger.debug(sms_code_str)
    #发送短信验证码
    # result=CCP().send_template_sms(mobile,[sms_code_str,constants.SMS_CODE_REDIS_EXPIRES/5],"1")
    # if result !=0:
    #     return jsonify(errno=RET.THIRDERR, errmsg="发送短信失败")
    #保存验证码到redis
    try:
        redis_store.set("SMS_"+mobile,sms_code_str,constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    return jsonify(errno=RET.OK, errmsg="发送短信成功")


#生成图片验证码
@passport_blu.route('/image_code')
def get_image_code():
    """
    生成图片验证码
    :return:
    """
    #从返回拿去image
    image_code_id=request.args.get("imageCodeId",None)
    current_app.logger.debug(image_code_id)
    if not image_code_id:
        return abort(403)
    #获取图片验证码的名字，字体，图片
    name,text,image= captcha.generate_captcha()

    try:
        #将信息缓存在redis
        redis_store.set("ImageCodeId_"+image_code_id,text,constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        #打印日志
        current_app.logger.error(e)
        #抛出异常
        abort(500)
    #指定类型
    response=make_response(image)
    response.headers["Content-Type"]="image/jpg"
    return response






