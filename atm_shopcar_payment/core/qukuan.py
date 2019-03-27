from db import db_file_write
from lib import log_user
import os,time
Path1=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
log1=r"atm_shopcar_payment\log\取款.log"
log2=r"atm_shopcar_payment\log\流水.log"
Logpath=os.path.join(Path1,log1)
Logpath1=os.path.join(Path1,log2)
def qukuan(name,dic_baihu,*args):

    logger=log_user.getlog(Logpath,"qukuan")
    logger1 = log_user.getlog(Logpath1, "qukuan2")
    dic1={}
    while True:
        money=input("请输入你要取款的金额: ")
        if money.isdigit():
            now_money=int(dic_baihu[name]["money"]) - int(money)
            if now_money >= 0:
                    dic1[name]={
                        "pwd": dic_baihu[name]["pwd"],
                        "money": now_money, "xyk_y": dic_baihu[name]["xyk_y"],
                        "xyk": dic_baihu[name]["xyk"],
                        "xyk_time": dic_baihu[name]["xyk_time"],
                        "logging_time": dic_baihu[name]["logging_time"]
                    }
                    dic_baihu.update(dic1)

                    jieguo = db_file_write.db_write(dic_baihu)
                    if jieguo == True:
                        print("正在取款中......")
                        time.sleep(1)
                        print("正在更新用户信息......")
                        time.sleep(1)
                        print("""
                        -----------------------    
                            取款成功
                            你的名字: %s
                            你的余额: %s
                            信用卡可用额度: %s
                        -----------------------
                            """ % (name, dic_baihu[name]["money"], \
                                   dic_baihu[name]["xyk_y"]))
                        time.sleep(2)
                        logger.info("%s取款%s" %(name,money))
                        logger1.info("%s取款%s" % (name, money))
                        break
                    else:
                        print("取款失败")
                        logger.error("%s取款%s错误" % (name, money))
            else:
                print("""
                -------------------------------
                        取款失败，您的余额不足！！！
                        你的姓名: %s
                        你的余额: %s
                        信用卡可用额度 : %s
                -------------------------------
                        """ % (name, dic_baihu[name]["money"], \
                            dic_baihu[name]["xyk_y"]))
                logger.error("%s取款%s大于余额" % (name, money))
                time.sleep(2)

        else:
            print("钱是数字")
            logger.error("%s输入错误" % (name))
            continue