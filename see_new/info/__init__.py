from redis import StrictRedis
from flask_sqlalchemy import SQLAlchemy
from config import config_dict
from flask_wtf.csrf import CSRFProtect
from flask import Flask
from flask_session import Session
from logging.handlers import RotatingFileHandler

import logging

# 初始化数据库
db = SQLAlchemy()
redis_store = None #type:StrictRedis
def create_app(config_name):
    # 创建app对象
    app =Flask(__name__)
    #通过config_name获取配置类
    config = config_dict.get(config_name)
    # 配置日志传入日志
    setup_app(config.LOGIN_LEVEL)
    # 加载配置类到app
    app.config.from_object(config)
    # 创建SQLAlchemy对象,关联app
    db.init_app(app)
    #初始化redis
    global redis_store
    redis_store=StrictRedis(host=config.REDIS_HOST,port=config.REDIS_PORT,password=config.REDIS_PASSWD,decode_responses=True)
    #开启CSRF防护，只做服务器验证功能
    CSRFProtect(app)
    #设置session保存位置
    Session(app)
    # 注册index_blu蓝图到app
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)
    return app

#记录日志信息方法
def setup_app(config_name):
    # 设置日志的记录等级,常见等级有: DEBUG<INFO<WARING<ERROR
    logging.basicConfig(level=config_name)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10,encoding="utf-8")
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)