from db import db_file_write
import os,time
from lib import log_user
Path1=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
log1=r"atm_shopcar_payment\log\注册.log"
Logpath=os.path.join(Path1,log1)
def user_zhuce(*args):
    logger=log_user.getlog(Logpath,"zhuce")
    name=args[0]
    dic_baihu=args[1]
    dic1={}
    tag=True
    while tag:
        pwd=input("请输入登录密码：").strip()
        if pwd.isdigit() and len(pwd) == 6:
             while tag:
                pwd2 = input("请再次输入登录密码：").strip()
                if pwd == pwd2:
                    while tag:
                        money=input("请输入你要存入的余额： ")
                        if not money.isdigit():
                            print("钱是数字")
                            continue
                        else:

                            while tag:
                                xyk=input("你的信用卡额度: ")
                                if not xyk.isdigit():
                                    print("信用卡额度是数字")
                                    continue
                                else:
                                     dic1[name]={

                                         "pwd": pwd2, "money": money,
                                         "xyk_y": xyk,
                                         "xyk": xyk,
                                         "xyk_time": "0",
                                         "logging_time": "0"
                                         }
                                     dic_baihu.update(dic1)

                                     jieguo=db_file_write.db_write(dic_baihu)
                                     if jieguo == True:
                                         print("注册成功,需要重新登陆....")
                                         time.sleep(1)
                                         logger.info("%s注册成功" %name)
                                         tag = False
                                         return jieguo
                else:
                    print("两次密码不一致")
                    logger.error("%s密码输入不一致" % name)
                    continue
        else:
            print("请输入6位数密码")
