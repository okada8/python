from django.shortcuts import HttpResponse
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from meiduo_mall.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from . import constants,serializers
from celery_tasks.sms.tasks import send_sms_code
from rest_framework import status
from users.models import User
# from meiduo_mall.libs.yuntongxun.sms import CCP
import random,logging
# Create your views here.
logger=logging.getLogger('django')


#注册时需要图片验证码
class ImageCodeView(APIView):
    """
    图片验证码，注册页面刚点开，需要主动向后端请求一个图片验证码，后端返回图片验证码后，要把图片验证码信息保存在redis
    regist.js会请求
    """
    def get(self,request,image_code_id):#image_code_id是前端自动生成的一个uuid
        #获取图片验证码的名字，内容，图片
        name,text,image=captcha.generate_captcha()#这是一个外部的包
        #获取redis的一个对象verify_codes（配置文件中定义的名字）
        redis_conn=get_redis_connection("verify_codes")#这是一个redis对象  type:object
        #将图片验证码的id，内容保存到redis，并定义时间
        redis_conn.setex("img_%s"%image_code_id,constants.IMAGE_CODE_REDIS_EXPRIES,text)
        #将图片返回,定义返回类型
        logger.info('图片验证码是%s'%text)
        return HttpResponse(image,content_type="images/jpg")#要给前端说明这是图片类型

#注册时手机要收短信验证码
class SMSCodeView(GenericAPIView):
    """短信验证码"""
    #定义序列化器是哪个序列化器，然后获取该序列化器的一个对象
    serializer_class = serializers.CheckImageCodeSerialzier #type:object
    def get(self,request,mobile):
        #调用GenericAPIView的get_serializer方法帮助我们校验
        #mobile字段被放在kwargs中
        serializer=self.get_serializer(data=request.query_params)
        #在校验过程中有异常就抛出异常，要先检验图片验证码是否正确，短信是否有发过
        serializer.is_valid(raise_exception=True)#会用我们自己定义的序列化器中的检验方法
        #生成短信验证码
        sms_code='%06d'%random.randint(0,999999)

        #保存验证码和发送记录
        #拿到redis
        redis_conn=get_redis_connection('verify_codes')
        #为了减少和数据库交互的次数，因而使用另一种方法redis管道pipeline,只需要和redis交互一次
        pl=redis_conn.pipeline()
        pl.setex('sms_%s' %mobile,constants.IMAGE_CODE_REDIS_EXPRIES,sms_code)
        pl.setex('send_flag_%s'%mobile,constants.SEND_SMS_CODE_INTERVAL,1)
        pl.execute()
        logger.info('%s的验证码是:%s' %(mobile,sms_code))

        #将短信记录保存，300秒过期
        # redis_conn.setex('sms_%s' %mobile,constants.IMAGE_CODE_REDIS_EXPRIES,sms_code)
        #1代表发送过，60s
        # redis_conn.setex('send_flag_%s'%mobile,constants.SEND_SMS_CODE_INTERVAL,1)

        #发送短信需要第三方包云通讯
        #拿到云通讯对象
        # ccp=CCP()
        #时间转字符串
        # time=str(constants.SMS_CODE_REDIS_EXPIRES/60)
        #发送短信
        # ccp.send_template_sms(mobile,[sms_code,time],constants.SMS_CODE_TEMP_ID)
        #使用celery发布异步任务
        send_sms_code.delay(mobile,sms_code)
        #返回
        return Response({'message':'OK'})


#忘记密码后，因为手机号码会由后端提供，只能根据access_token来发送短信find_password.js会请求
class SMSCodeByToKenView(APIView):
    def get(self,request):
        #获取校验access_token
        access_token=request.query_params.get('access_token')
        #如果token不存在
        if not access_token:
            return  Response({"messsge":"缺少access token"},status=status.HTTP_400_BAD_REQUEST)
        #从access_token中取出手机号码
        mobile=User.check_send_sms_token(access_token)
        if mobile is None:
            return Response({"messsge": "无效的access token"}, status=status.HTTP_400_BAD_REQUEST)
        #判断手机号码发送短信的次数,查看redis中是否有发送过短信的标志
        redis_conn = get_redis_connection("verify_codes")
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return Response({"messsge": "发送短信过于频繁"}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        #生成短信验证码
        sms_code = '%06d' % random.randint(0, 999999)
        #发送短信验证码
        pl = redis_conn.pipeline()
        pl.setex('sms_%s' % mobile, constants.IMAGE_CODE_REDIS_EXPRIES, sms_code)
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        pl.execute()
        logger.info('%s的验证码是:%s' % (mobile, sms_code))
        # 使用celery发布异步任务
        send_sms_code.delay(mobile, sms_code)
        # 返回
        return Response({'message': 'OK'})





























