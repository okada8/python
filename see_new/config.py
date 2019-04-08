from redis import StrictRedis
import logging

class Config(object):
    DEBUG=True
    SECRET_KEY="ucpM5PASrY/TwTE3lP2yGf8pB2IGy+4O1nSFyAq2PGo6EqxpAl7rdtoZZ0sYqtLG"
    #为数据库添加配置
    SQLALCHEMY_DATABASE_URI="mysql://root:qwer1234@127.0.0.1:3306/my_new_web"
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    #如果配置为ture，会自动执行db.session.commit()
    SQLALCHEMY_COMMIT_ON_TEARDOWN=True
    #设置redis
    REDIS_HOST="127.0.0.1"
    REDIS_PORT=6379
    REDIS_PASSWD="qwer1234"
    #session保存位置
    SESSION_TYPE="redis"
    # 是否开启session签名
    SESSION_USE_SIGNER = True
    #指定session保存redis
    SESSION_REDIS=StrictRedis(host=REDIS_HOST,port=REDIS_PORT,password=REDIS_PASSWD)
    # 设置过期
    SESSION_PERMANENT = False
    #设置过期时间
    PERMANENT_SESSION_LIFETIME = 86400 * 2
    #设置日志等级
    LOGIN_LEVEL=logging.DEBUG

class Developement(Config):
    """开发环境下配置"""
    pass


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    #设置日志等级
    LOGIN_LEVEL = logging.WARNING

class TestingConfig(Config):
    """单元测试环境配置"""
    TESTING=True

config_dict={
    "developement":Developement,
    "productionconfig":ProductionConfig,
    "testingconfig":TestingConfig
    }

