from celery import Celery

# 为celery使用django配置文件进行设置
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'


# 创建Celery对象
celery_app = Celery('celery_tasks')

# 加载配置信息
celery_app.config_from_object('celery_tasks.config')

# 自动发现任务
celery_app.autodiscover_tasks(['celery_tasks.sms'])