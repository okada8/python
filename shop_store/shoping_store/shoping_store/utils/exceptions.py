#关于异常处理
#修改Django REST framework的默认异常处理方法，补充处理数据库异常和Redis异常
from  rest_framework.response import Response
from rest_framework import status
from rest_framework.views import exceptions as drf_exception_handler
from django.db import DatabaseError
from redis.exceptions import RedisError
import logging

logger=logging.getLogger('django')

def handler_excption(exc,context):
    """
    自定义异常处理
    :param exc:异常
    :param context:抛出异常的下文
    :return: response相应对象
    """
    #调用drf框架原生的异常处理方法
    response=drf_exception_handler(exc,context)
    if response is None:
        view=context['view']
        if isinstance(exc,DatabaseError) or isinstance(exc,RedisError):
            #数据库异常
            logger.error('[%s] %s' %(view,exc))
            response=Response({'message': '服务器内部错误'}, status=status.HTTP_507_INSUFFICIENT_STORAGE)

    return response


