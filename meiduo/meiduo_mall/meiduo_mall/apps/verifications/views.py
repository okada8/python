from django.shortcuts import HttpResponse,render
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from meiduo_mall.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from . import constants,serializers
from celery_tasks.sms.tasks import send_sms_code
# from meiduo_mall.libs.yuntongxun.sms import CCP
import random,logging
# Create your views here.
logger=logging.getLogger('django')



class ImageCodeView(APIView):
    """
    图片验证码
    """
    def get(self,request,image_code_id):
        #获取图片验证码的名字，内容，图片
        name,text,image=captcha.generate_captcha()
        #获取redis的一个对象verify_codes（配置文件中定义的名字）
        redis_conn=get_redis_connection("verify_codes")
        #将图片验证码的id，内容保存到redis，并定义时间
        redis_conn.setex("img_%s"%image_code_id,constants.IMAGE_CODE_REDIS_EXPRIES,text)
        #将图片返回,定义返回类型
        logger.info('图片验证码是%s'%text)
        return HttpResponse(image,content_type="images/jpg")


class SMSCodeView(GenericAPIView):
    """短信验证码"""
    #定义序列化器是哪个序列化器，然后获取该序列化器的一个对象
    serializer_class = serializers.CheckImageCodeSerialzier
    def get(self,request,mobile):
        #调用GenericAPIView的get_serializer方法帮助我们校验
        #mobile字段被放在kwargs中
        serializer=self.get_serializer(data=request.query_params)
        #在校验过程中有异常就抛出异常
        serializer.is_valid(raise_exception=True)
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


























