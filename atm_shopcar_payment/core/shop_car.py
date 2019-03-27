from core import payment
from lib import log_user
import os,time
Path1=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
log1=r"atm_shopcar_payment\log\购物车.log"
Logpath=os.path.join(Path1,log1)
def shopcar(name,dic_baihu,*args):

    logger=log_user.getlog(Logpath,"shop_car")
    shope_car1 = {}
    tag = True
    while tag:
        print("""
                    欢迎来到苹果中国
        ---------------------------------------
                  商品列表              单价
                
                1.iphone xs max       10000
                2.iphone xr           9000
                3.iphone x            6000
                4.mac                 12000
            5.结算                         6.退出
        ----------------------------------------
             """)
        choice = int(input("请选择要购买的商品: "))
        time.sleep(1)
        if choice in [1, 2, 3, 4]:
            number = input("请输入你要购买的数量: ")
            time.sleep(1)
            if choice == 1:
                logger.info("%s购买了iphone xs max%s个"%(name,number))
                shope_car1["iphone xs max"] = {"price": 10000, "number": number}
            elif choice == 2:
                logger.info("%s购买了iphone xr%s个" % (name, number))
                shope_car1["iphone xr"] = {"price": 9000, "number": number}
            elif choice == 3:
                logger.info("%s购买了iphone x%s个" % (name, number))
                shope_car1["iphone x"] = {"price": 6000, "number": number}
            elif choice == 4:
                logger.info("%s购买了mac%s个" % (name, number))
                shope_car1["mac"] = {"price": 12000, "number": number}
        else:
            if choice == 5:
                logger.info("%s开始结算" % (name))
                payment.jiesuan(name, dic_baihu, shope_car1)
            elif choice == 6:
                logger.info("%s退出" % (name))
                tag = False

            else:
                logger.error("%s输入错误" % (name))
                print("请输入1-6")