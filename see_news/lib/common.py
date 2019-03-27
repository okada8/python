from db import DB_handler
from conf import settings
import hashlib
import time
import random
import re
import logging.config
logging_user=False
username=None

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
            'user_handler': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',  # Rotatin日志轮转 保存到文件
                'formatter': 'standard',
                'filename': settings.USER_LOG,  # 日志文件的路径
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
            'user': {
                'handlers': ['user_handler'],  # 这里把上面定义的两个handler都加上，即log数据既写入文件又打印到屏幕
                'level': 'DEBUG',
            },
        },
    }
    logging.config.dictConfig(LOGGING_DIC)
    return logging.getLogger(name)

logger2=get_logging("user")

def logginger():
    global logging_user,username
    dic_user=DB_handler.get_user_read()
    while True:
        user_name=input("请输入你的姓名: ").strip()
        if user_name not in dic_user:
            print("""
                该用户不存在！！！
                1.注册
                2.重新输入
                3.退出
                """)
            choice=input("请选择: ")
            if choice == "1":
                jieguo=zhuce(dic_user)
                if jieguo == True:
                    return
            elif choice == "2":
                continue
            elif choice == "3":
                return
            else:
                print("你输入的不正确!!!")
        else:
            if dic_user[user_name]["lock"] == False:
                count=0
                if time.time()-dic_user[user_name]["logger_time"] >=300:
                    while count <= 2:
                        pwd=input("请输入您的密码：").strip()
                        pwd1=hashlib_pwd(pwd)
                        if pwd1 == dic_user[user_name]["pwd"]:
                            print("登陆成功")
                            dic_user[user_name]["logger_time"]=0
                            DB_handler.get_user_write(dic_user)
                            logging_user = True
                            username=user_name
                            return dic_user[user_name]["type"],user_name
                        else:
                            print("密码不正确，请重新输入")
                            count+=1
                    else:
                        print("您输入次数过多，账户已被锁定300秒")
                        dic_user[user_name]["logger_time"] = time.time()
                        DB_handler.get_user_write(dic_user)
                else:
                    print("账户之前被锁定时间未超过300秒")
                    continue
            else:
                print("您的账户已被管理员锁定，请联系管理员")
                continue

def hashlib_pwd(pwd):
    m=hashlib.md5()
    m.update(pwd.encode("utf-8"))
    return m.hexdigest()

def yanzheng(fun):
    def warpper(*args):
        news_name=args[0]
        if logging_user == False:
            type,user_name =logginger()
            fun(news_name,user_name)
        else:
            fun(news_name,username)
    return warpper

def zhuce(dic_user):
    tag = True
    while tag:
        user_name=input("请输入您要注册的姓名：").strip()
        if user_name in dic_user:
            print("该姓名存在")
            continue
        pwd1 = input("请输入密码：").strip()
        pwd2 = input("请在此输入密码：").strip()
        if pwd1 == pwd2:
            pwd3 = hashlib_pwd(pwd2)
            while tag:
                emile = input("请输入邮箱：").strip()
                j = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", emile)
                if j != []:
                    while tag:
                        yanzhengma1 = yanzhengma()
                        print("验证码：%s" % yanzhengma1)
                        yanzhengma2 = input("请输入验证码，区分大小写: ").strip()
                        if yanzhengma2 == yanzhengma1:
                            print("""
                            用户名：%s
                            密码：%s
                            邮箱:%s
                            """ % (user_name, pwd2, emile))
                            dic_user[user_name] = {"pwd": pwd3,
                                              "email":emile,
                                              "logger_time":0,
                                              "lock":False,
                                              "type":0
                                              }
                            res=DB_handler.get_user_write(dic_user)
                            jieguo=DB_handler.user_zhuce_ini(user_name)
                            if res ==True and jieguo == True:
                                print("注册成功")
                                logger2.info("%s注册成功" %user_name)
                                return  True
                            else:
                                print("注册失败，联系管理员")
                                tag =False
                        else:
                            print("验证码输入错误!")
                            continue
                else:
                    print("邮箱错误")
                    continue
        else:
            print("密码输入错误")
            continue

def yanzhengma():
    list1 = ""
    for i in range(4):
        j = random.randrange(0, 4)
        if j == 1:
            a = random.randrange(0, 10)
            list1 = list1 + str(a)
        elif j == 2:
            a = chr(random.randrange(65, 90))
            list1 = list1 + a
        else:
            a = chr(random.randrange(97, 122))
            list1 = list1 + a
    return list1

if __name__ == '__main__':
    logginger()