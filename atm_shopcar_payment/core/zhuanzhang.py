import os,time
from db import db_file_write
from lib import log_user
Path1=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
log1=r"atm_shopcar_payment\log\转账.log"
log2=r"atm_shopcar_payment\log\流水.log"
Logpath=os.path.join(Path1,log1)
Logpath1=os.path.join(Path1,log2)
def zhuanzhang(name,dic_baihu,dic_heihu):

    logger=log_user.getlog(Logpath,"zhuanzhang")
    logger1 = log_user.getlog(Logpath1, "zhuanzhang2")
    tag=True
    dic1={}
    dic2={}

    while tag:
        own_name=input("你要转给谁：")
        print("正在查找用户信息......")
        time.sleep(2)
        if own_name in dic_baihu:
            while tag:
                money=input("请输入转多少: ")
                if money.isdigit():
                    now_name_money=int(dic_baihu[name]["money"])-int(money)
                    now_own_mone=int(dic_baihu[own_name]["money"])+int(money)
                    if now_name_money > 0:
                        dic1.clear()
                        dic1[name]={

                            "pwd": dic_baihu[name]["pwd"],
                            "money":str(now_name_money),
                            "xyk_y": dic_baihu[name]["xyk_y"],
                            "xyk": dic_baihu[name]["xyk"],
                            "xyk_time": dic_baihu[name]["xyk_time"],
                            "logging_time": dic_baihu[name]["logging_time"]

                        }
                        dic1[own_name]={

                            "pwd": dic_baihu[name]["pwd"],
                            "money": str(now_own_mone),
                            "xyk_y": dic_baihu[name]["xyk_y"],
                            "xyk": dic_baihu[name]["xyk"],
                            "xyk_time": dic_baihu[name]["xyk_time"],
                            "logging_time": dic_baihu[name]["logging_time"]

                        }
                        dic_baihu.update(dic1)

                        jieguo = db_file_write.db_write(dic_baihu)
                        if jieguo == True:
                            print("正在查询信息......")
                            time.sleep(1)
                            print("正在转账中........")
                            time.sleep(1)
                            print("正在更新账户信息......")
                            time.sleep(1)
                            print("""
                        ------------------------------       
                                转账成功!!!
                                你的名字: %s
                                你的余额: %s
                                你的信用卡可用额度: %s
                        -------------------------------     
                                """ % (name, dic_baihu[name]["money"], \
                                       dic_baihu[name]["xyk_y"]))
                            time.sleep(2)
                            logger.info("%s给%s转了%s" %(name,own_name,money))
                            logger1.info("%s给%s转了%s" % (name, own_name, money))
                            tag=False
                        else:
                            print("存款错误")
                            logger.error("%s给%s转了%s出现错误" % (name, own_name, money))
                    else:
                        print("您的余额不足")
                        logger.error("%s余额不足" % (name))
                else:
                    print("钱是数字")
                    logger.error("%s输入错误" % (name))
                    continue

        elif own_name in dic_heihu:

                    while tag:
                        money = input("请输入转多少: ")
                        if money.isdigit():
                            now_name_money = int(dic_baihu[name]["money"]) - int(money)
                            now_own_mone = int(dic_heihu[own_name]["money"]) + int(money)
                            if now_name_money >0:

                                dic2.clear()
                                dic1.clear()
                                dic1[name] = {

                                    "pwd": dic_baihu[name]["pwd"],
                                    "money": str(now_name_money),
                                    "xyk_y": dic_baihu[name]["xyk_y"],
                                    "xyk": dic_baihu[name]["xyk"],
                                    "xyk_time": dic_baihu[name]["xyk_time"],
                                    "logging_time": dic_baihu[name]["logging_time"]
                                }
                                dic2[own_name] = {

                                    "pwd": dic_heihu[own_name]["pwd"],
                                    "money": str(now_own_mone),
                                    "xyk_y": dic_heihu[own_name]["xyk_y"],
                                    "xyk": dic_heihu[own_name]["xyk"],
                                    "xyk_time": dic_heihu[own_name]["xyk_time"],
                                    "logging_time": dic_heihu[own_name]["logging_time"]
                                }
                                dic_baihu.update(dic1)
                                dic_heihu.update(dic2)

                                jieguo =db_file_write.db_write(dic_baihu,dic_heihu)
                                if jieguo == True:
                                    print("正在查询信息......")
                                    time.sleep(1)
                                    print("正在转账中........")
                                    time.sleep(1)
                                    print("正在更新账户信息......")
                                    time.sleep(1)
                                    print("""
                                ------------------------------        
                                        转账成功
                                        你的名字 : %s
                                        你的余额: %s
                                        你的信用卡 : %s
                                ------------------------------        
                                        """ % (name, dic_baihu[name]["money"], \
                                               dic_baihu[name]["xyk_y"]))
                                    logger.info("%s给%s转了%s" % (name, own_name, money))
                                    logger1.info("%s给%s转了%s" % (name, own_name, money))
                                    tag=False
                                else:
                                    print("转账错误")
                                    logger.error("%s给%s转了%s出现错误" % (name, own_name, money))
                            else:
                                print("您的余额不足")
                                logger.error("%s余额不足" % (name))
                        else:
                            print("钱是数字")
                            logger.error("%s输入错误" % (name))
                            continue
        else:
            print("%s不存在,请重新输入" %own_name)
            time.sleep(2)
            logger.error("%s不存在" % (own_name))