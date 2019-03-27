from db import db_file_write
from lib import log_user
import os,time
Path1=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
log1=r"atm_shopcar_payment\log\存款.log"
log2=r"atm_shopcar_payment\log\流水.log"
Logpath=os.path.join(Path1,log1)
Logpath1=os.path.join(Path1,log2)
def cunkuan(name,dic_baihu,*args):
    logger=log_user.getlog(Logpath,"cunkuan")
    logger1 = log_user.getlog(Logpath1, "cunkuan2")
    dic1={}
    while True:
        money=input("请输入您要存入的金额: ")
        if money.isdigit():
           now_money=int(money)+int(dic_baihu[name]["money"])
           dic1[name]={

               "pwd": dic_baihu[name]["pwd"], "money": str(now_money),
               "xyk_y": dic_baihu[name]["xyk_y"],
               "xyk": dic_baihu[name]["xyk"],
               "xyk_time":dic_baihu[name]["xyk_time"],
               "logging_time": dic_baihu[name]["logging_time"]
            }
           dic_baihu.update(dic1)
           jieguo=db_file_write.db_write(dic_baihu)
           if jieguo == True:
               print("正在存款中.....")
               time.sleep(1)
               print("正在更新用户信息.....")
               time.sleep(1)
               print("""
               -----------------------
                   存款成功！！！
                   你的姓名 : %s
                   你的余额: %s
                   信用卡可用额度 : %s
               -----------------------
                   """ % (name, dic_baihu[name]["money"], \
                          dic_baihu[name]["xyk"]))
               time.sleep(2)
               logger1.info("%s存入了%s" % (name, money))
               logger.info("%s存入了%s" %(name,money))
               break
           else:
               print("存款失败")
               logger.error("%s存入%s错误" % (name, money))
        else:
            print("请输入数字")
            logger.error("%s输入错误" % (name))
            continue