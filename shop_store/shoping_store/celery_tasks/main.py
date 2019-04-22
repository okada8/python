from celery import Celery

# 创建Celery对象
celery_app = Celery('celery_tasks')

# 加载配置信息
celery_app.config_from_object('celery_tasks.config')

# 自动发现任务
celery_app.autodiscover_tasks(['celery_tasks.sms'])

#开启
