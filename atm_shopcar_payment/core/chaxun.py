import os,time
from lib import log_user
Path1=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
log1=r"atm_shopcar_payment\log\查询.log"
Logpath=os.path.join(Path1,log1)
def chaxun(name,dic_baihu,*args):
    logger=log_user.getlog(Logpath,"chaxun")
    print("正在查询中.....")
    time.sleep(2)
    print("""
 ------------------------   
    你的姓名: %s
    你的余额: %s
    信用卡可用额度: %s
 ------------------------   
    """ %(name,dic_baihu[name]["money"],\
          dic_baihu[name]["xyk_y"]))
    time.sleep(2)
    logger.info("%s查询了余额" %name)