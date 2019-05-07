
import os

from lib import log_user
from core import chaxun
from core import zhuanzhang
from core import qukuan
from core import cunkuan
from core import shop_car
from core import xyk
Path1=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
log1=r"atm_shopcar_payment\log\选择业务.log"
Logpath=os.path.join(Path1,log1)
def app(*args):

    name=args[0]
    logger=log_user.getlog(Logpath,"choice")
    dic={"1":chaxun.chaxun,"2":zhuanzhang.zhuanzhang,\
         "3":qukuan.qukuan,"4":cunkuan.cunkuan,"5":shop_car.shopcar,
         "6":xyk.xyk_ye1}
    while True:
        print("""
---------------------    
    【1】查询
    【2】转账
    【3】取款
    【4】存款
    【5】购物
    【6】信用卡业务
    【7】退出
-----------------------
""")
        choice=input("你的选择: ")
        if choice in dic:
            dic[choice](*args)
            logger.info("%s选择了%s" %(name,dic[choice]))
        else:
            logger.info("%s选择了退出" % (name))
            break




