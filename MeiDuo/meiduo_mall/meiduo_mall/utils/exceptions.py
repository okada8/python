from rest_framework.views import exception_handler as drf_exception_handler
from django.db import DatabaseError
from redis.exceptions import RedisError
from rest_framework.response import Response
from rest_framework import status
import logging

logger=logging.getLogger('django')
def exception_hanler(exc,context):
    """
    自定义异常
    :param exc:异常
    :param context:抛出异常的上下文
    :return: response响应对象
    """
    #调用drf框架原生的异常处理方法
    response=drf_exception_handler(exc,context)
    if response is None:
        view=context['view']
        if isinstance(exc,DatabaseError) or isinstance(exc,RedisError):
            logger.error('[%s] %s' %(view,exc))
            response=Response({'message':'服务器内部错误'},status=status.HTTP_507_INSUFFICIENT_STORAGE)
    return response



