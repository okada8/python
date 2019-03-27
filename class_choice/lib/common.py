from interface import admin_interface, student_interface, teacher_interface
from conf import settings
from db import DB_handler
import logging.config
Logging = False
name=None

# 注册功能
def register(startname):
    while True:
        user_name = input("请输入注册用户名(q退出)：").strip()
        if user_name == "q":break
        if not user_name:
            print("用户名不能为空")
            continue
        pwd = input("请输入密码：").strip()
        if not pwd:
            print("密码不能为空")
            continue
        pwd1 = input("请再次输入密码：").strip()
        pwd2 = DB_handler.halib_file(pwd1)
        if not pwd1:
            print("密码不能为空")
            continue
        if pwd != pwd1:
            print("两次密码不一致")
            continue
        # 将数据按照不同的用户传给对应的接口层
        if startname == "admin":
            obj = admin_interface.admin_resister(user_name, pwd2)
            if obj:
                print("管理员注册成功")
                logger = get_logging("admin")
                logger.info("%s管理员注册成功" % (user_name))
                return
            else:
                print("用户名已存在，")
        elif startname == "student":
            obj = student_interface.student_resister(user_name, pwd2)
            if obj:
                print("学生注册成功,请重新启动")
                logger=get_logging("student")
                logger.info("%s学生注册成功"%(user_name))
                exit(0)
            else:
                print("用户名已存在，")
        else:
            obj = teacher_interface.teacher_resister(user_name, pwd2)
            if not obj:
                print("老师注册成功")
                logger = get_logging("teacher")
                logger.info("%s老师注册成功" % user_name)
                return user_name
            else:
                print(obj)
# 登录功能
def login(startname):
    global Logging,name
    while True:
        username = input("请输入登录用户名：").strip()
        filenames = DB_handler.get_all_filename(startname.lower())
        if username in filenames:
            pwd = input("请输入登录密码：").strip()
            obj1 = DB_handler.halib_file(pwd)
            obj = DB_handler.load_obj_from_file(startname, username)
            pwd2 = getattr(obj, "pwd")
            if obj1 == pwd2:
                Logging = True
                print("登录成功！！！")
                name=obj
                return name
            print("密码错误！！！")
            continue
        while True:
                if startname == "student" or startname == "admin":
                    print("""
======================
    1.注册
    2.返回
======================           
                """)
                    choice = input("请选择：")
                    if choice == "1":
                        obj = register(startname)
                        if not obj:
                            return
                        elif choice == "2":
                            return
                        else:
                            print("输入错误！！！")
                else:
                    print("请联系管理员帮你注册")
                    return
#日志功能
def get_logging(name):
    standard_format = '[%(asctime)s][%(threadName)s:%(thread)d][task_id:%(name)s][%(filename)s:%(lineno)d]' \
                      '[%(levelname)s][%(message)s]'  # 其中name为getlogger指定的名字

    LOGGING_DIC = {
        'version': 1,  # 只能为1
        'disable_existing_loggers': False,  # 是否禁用已经存在的生成器,通常为False
        'formatters': {  # 不能修改 内部可以有多个格式处理器
            'standard': {  # 是格式处理器的名字 可以自定义
                'format': standard_format  # key不能修改
            },
        },
        'filters': {},
        'handlers': {  # key不能修改
            'console': {  # 处理的名字 可以修改
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',  # 打印到屏幕
                'formatter': 'standard'  # 指定处理器的格式
            },
            'admin_handler': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',  # Rotatin日志轮转 保存到文件
                'formatter': 'standard',
                'filename': settings.ADMIN_LOG,  # 日志文件的路径
                'maxBytes': 1024 * 1024 * 5,  # 日志大小 5M
                'backupCount': 5,  # 最多存在五个日志文件
                'encoding': 'utf-8',  # 日志文件的编码，再也不用担心中文log乱码了
            },
            'teacher_handler': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',  # Rotatin日志轮转 保存到文件
                'formatter': 'standard',
                'filename': settings.TEACHER_LOG,  # 日志文件的路径
                'maxBytes': 1024 * 1024 * 5,  # 日志大小 5M
                'backupCount': 5,  # 最多存在五个日志文件
                'encoding': 'utf-8',  # 日志文件的编码，再也不用担心中文log乱码了
            },
            'student_handler': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',  # Rotatin日志轮转 保存到文件
                'formatter': 'standard',
                'filename': settings.STUDENT_LOG,  # 日志文件的路径
                'maxBytes': 1024 * 1024 * 5,  # 日志大小 5M
                'backupCount': 5,  # 最多存在五个日志文件
                'encoding': 'utf-8',  # 日志文件的编码，再也不用担心中文log乱码了
            },
        },
        'loggers': {
            'admin': {
                'handlers': ['admin_handler'],  # 这里把上面定义的两个handler都加上，即log数据既写入文件又打印到屏幕
                'level': 'DEBUG',
            },
            'teacher': {
                'handlers': ['teacher_handler'],  # 这里把上面定义的两个handler都加上，即log数据既写入文件又打印到屏幕
                'level': 'DEBUG',
            },
            'student': {
                'handlers': ['student_handler'],  # 这里把上面定义的两个handler都加上，即log数据既写入文件又打印到屏幕
                'level': 'DEBUG',
            },
        },
    }
    logging.config.dictConfig(LOGGING_DIC)
    return logging.getLogger(name)

# 登录装饰器
def auth(func):
    def warpper(*args, **kwargs):
        if Logging == True:
            res = func(*args, **kwargs)
            return res
        else:
            obj = login(*args, **kwargs)
            if obj:
                res = func(*args,**kwargs)
                return res
    return warpper

if __name__ == '__main__':
    pass

