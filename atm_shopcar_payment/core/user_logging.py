from db import db_file_write
from core import zhuce
from core import xuanze
from lib import log_user
import time,os
Path1=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
log1=r"atm_shopcar_payment\log\登录.log"
Logpath=os.path.join(Path1,log1)
def loging(*args):
    logger=log_user.getlog(Logpath,"logger")
    count = 0
    dic_baihu=args[0]
    dic_heihu=args[1]
    dic1={}
    logger.info("进入登录循环")
    while True:

        print("""
-----------------------------------------        
        欢迎来到建设银行ATM终端
        公安局温馨提示您请关好门
        提示：同账户密码输错三次将会被系统
        锁定5分钟！！！
        
        
1.登录                              2.退出
-----------------------------------------        
        """)
        choice8=input("请选择：")
        if choice8=="1":

            user_name=input("你的名字: ").strip()
            if user_name not in dic_heihu and  user_name not in dic_baihu:
                    print("""
                    你输入的名字不存在
                    1.注册
                    2.退出
                    """)
                    choice=input("请选择: ").strip()
                    if choice == "1":
                        jieguo=zhuce.user_zhuce(user_name,dic_baihu)
                        if jieguo == True:
                            count = 0
                            continue
                    else:
                        break
            if user_name in dic_baihu:
                user_pawd = input("请输入密码: ").strip()
                if count < 2:
                    if user_pawd == dic_baihu[user_name]["pwd"]:
                        print("登录成功")
                        time.sleep(1)
                        logger.info("%s登录成功" %user_name)
                        xuanze.app(user_name,dic_baihu,dic_heihu)
                    else:
                        print("密码错误")
                        logger.error("%s密码错误" % user_name)
                        count += 1
                        continue
                if count >= 2:
                    print("你的账户已经锁定")
                    time.sleep(2)
                    logger.error("%s登录锁定" % user_name)
                    dic1[user_name] = {
                            "pwd":dic_baihu[user_name]["pwd"],
                        "money":dic_baihu[user_name]["money"],
                        "xyk_y":dic_baihu[user_name]["xyk_y"],
                            "xyk":dic_baihu[user_name]["xyk"],
                        "xyk_time":dic_baihu[user_name]["xyk_time"],
                            "logging_time": time.time()}
                    dic_heihu.update(dic1)
                    dic_baihu.pop(user_name)

                    db_file_write.db_write(dic_baihu, dic_heihu)

            else:
                nowtime=time.time()
                if nowtime-float(dic_heihu[user_name]["logging_time"])>300:

                    user_pawd = input("请输入密码: ").strip()
                    if count < 2:
                        if user_pawd == dic_heihu[user_name]["pwd"]:

                            dic1.clear()
                            dic1[user_name] = {
                                 "pwd":dic_heihu[user_name]["pwd"],
                        "money":dic_heihu[user_name]["money"],
                        "xyk_y":dic_heihu[user_name]["xyk_y"],
                            "xyk":dic_heihu[user_name]["xyk"],
                        "xyk_time":dic_heihu[user_name]["xyk_time"],
                            "logging_time": time.time()
                            }
                            dic_baihu.update(dic1)
                            dic_heihu.pop(user_name)

                            jieguo=db_file_write.db_write(dic_baihu, dic_heihu)
                            if jieguo == True:
                                print("成功解除锁定，需要程序重新启动")
                                logger.info("%s解锁成功"%user_name)
                                exit()
                            else:
                                print("登陆错误")
                        else:
                            print("密码错误")
                            logger.error("%s密码错误" % user_name)
                            count += 1
                            continue
                    else:

                        print("你的账户已经锁定")
                        time.sleep(1)
                        logger.error("%s登录锁定" % user_name)
                        dic1.clear()
                        dic1[user_name] = {
                                       "pwd":dic_heihu[user_name]["pwd"],
                        "money":dic_heihu[user_name]["money"],
                        "xyk_y":dic_heihu[user_name]["xyk_y"],
                            "xyk":dic_heihu[user_name]["xyk"],
                        "xyk_time":dic_heihu[user_name]["xyk_time"],
                            "logging_time":time.time()}
                        dic_heihu.update(dic1)

                        db_file_write.db_write(dic_heihu)
                else:
                    print("你的账户距离上次锁定小于300秒,请稍后再试")
                    time.sleep(1)
                    logger.error("%s登录之前就已锁定" % user_name)


        else:
            exit()

