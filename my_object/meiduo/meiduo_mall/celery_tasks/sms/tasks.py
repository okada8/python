# 封装任务函数
from celery_tasks.main import celery_app
from .yuntongxun.sms import CCP
from . import constants


@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    # 拿到云通讯对象
    ccp = CCP()
    # 时间转字符串
    time = str(constants.SMS_CODE_REDIS_EXPIRES / 60)
    # 发送短信
    ccp.send_template_sms(mobile, [sms_code, time], constants.SMS_CODE_TEMP_ID)
