from  db import db_file_write
from lib import log_user
import time,os
Path1=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
log1=r"atm_shopcar_payment\log\结算.log"
log2=r"atm_shopcar_payment\log\流水.log"
Logpath=os.path.join(Path1,log1)
Logpath1=os.path.join(Path1,log2)
def jiesuan(name, dic_baihu,shope_car):
    logger=log_user.getlog(Logpath,"payment")
    logger1 = log_user.getlog(Logpath1, "jiesuan")
    tag=True
    l = []
    l1 = []
    dic = {}
    shop_car = {}
    shop_car.update(shope_car)
    sum_money2 = 0
    if len(shop_car)  > 1:
        logger.info("%s购物车商品是两种" % name)

        xyk_yue = int(dic_baihu[name]["money"]) + float(dic_baihu[name]["xyk_y"])
        user_yue = int(dic_baihu[name]["money"])
        user_xyk = float(dic_baihu[name]["xyk_y"])
        for k, v in shop_car.items():
            l.append(k)
            sum_money1 = int(v["number"]) * int(v["price"])
            sum_money2 += sum_money1

            s = " ".join([k, str(shop_car[k]["price"]),
                          str(shop_car[k]["number"]), str(sum_money1)])
            l.append(s)

        for i in range(len(l)):
            if i % 2 != 0:
                l1.append(l[i])

            s4 = "\n".join(l1)

        if sum_money2 > xyk_yue and sum_money2 > user_xyk and \
                sum_money2 > user_yue:
            logger.error("%s信用卡和余额不足以支付"%name)
            print("您的余额和信用卡都不足以支付订单")
            shop_car.clear()
            return
        else:
            print("""
-------------清单---------------------
商品名      单价    数量      总价
%s



                            共计:%s
--------------------------------------
        """ % (s4, sum_money2))
            time.sleep(1)
            while tag:
                print("""
                ------------------------------
                    请选择支付方式
                    1.余额支付
                    2.信用卡支付
                    3.余额加信用卡组合支付
                    4.取消支付(系统会自动清空购物车)
                -------------------------------
                    """)
                choice3 = input("请选择: ")
                if choice3 == "1":
                    if user_yue < sum_money2:
                        logger.error("%s余额不足以支付" % name)
                        print("您目前余额为%s,不能支付请选择其他付款方式" % user_yue)
                        continue
                    else:
                        now_user_yue = user_yue - sum_money2

                        while tag:
                            choice4 = input("确认输入Y/y,退出输入N/n: ")

                            if choice4 in ["y", "Y"]:
                                dic[name] = {

                                    "pwd": dic_baihu[name]["pwd"],
                                    "money": now_user_yue,
                                    "xyk_y": dic_baihu[name]["xyk_y"],
                                    "xyk": dic_baihu[name]["xyk"],
                                    "xyk_time": dic_baihu[name]["xyk_time"],
                                    "logging_time": dic_baihu[name]["logging_time"]
                                }
                                dic_baihu.update(dic)
                                jieguo = db_file_write.db_write(dic_baihu)
                                print("正在支付中.....")
                                time.sleep(2)
                                if jieguo == True:
                                    logger.info("%s余额支付%s成功" % (name,sum_money2))
                                    logger1.info("%s余额支付%s成功" % (name, sum_money2))
                                    print("支付成功,即将返回上品列表")
                                    tag=False
                                else:
                                    logger.error("%s余额支付失败" % name)
                                    print("支付失败")
                            else:
                                tag = False

                        if user_xyk < sum_money2:
                                    print("您目前信用余额为%s,不能支付请选择其他付款方式" % user_xyk)
                                    logger.error("%s信用卡余额不足以支付" % name)
                                    continue
                        else:
                                    now_user_xyk = user_xyk - sum_money2

                                    while tag:
                                        choice4 = input("确认输入Y/y,退出输入N/n: ")
                                        if choice4 in ["y", "Y"]:

                                            dic[name] = {

                                                "pwd": dic_baihu[name]["pwd"],
                                                "money": dic_baihu[name]["money"],
                                                "xyk_y": now_user_xyk,
                                                "xyk": dic_baihu[name]["xyk"],
                                                "xyk_time": time.time(),
                                                "logging_time": dic_baihu[name]["logging_time"]

                                            }
                                            dic_baihu.update(dic)
                                            jieguo = db_file_write.db_write(dic_baihu)
                                            print("正在支付中.....")
                                            time.sleep(2)
                                            if jieguo == True:
                                                logger.info("%s信用卡支付%s成功" % (name,sum_money2))
                                                logger1.info("%s信用卡支付%s成功" % (name, sum_money2))
                                                print("支付成功,即将返回商品列表")
                                                time.sleep(1)

                                            else:
                                                logger.error("%s信用卡支付失败" % name)
                                                print("支付失败")
                                        elif choice4 in ["n", "N"]:
                                            logger.error("%s选择退出" % name)
                                            tag = False
                                        else:
                                            logger.error("%s输入错误" % name)
                                            print("输入错误,请重新输入")
                                            continue
                elif choice3 == "2":
                    if user_xyk < sum_money2:
                        print("您目前信用余额为%s,不能支付请选择其他付款方式" % user_xyk)
                        logger.error("%s信用卡余额不足以支付" % name)
                        continue
                    else:
                        now_user_xyk = user_xyk - sum_money2

                        while tag:
                            choice4 = input("确认输入Y/y,退出输入N/n: ")
                            if choice4 in ["y", "Y"]:

                                dic[name] = {

                                    "pwd": dic_baihu[name]["pwd"],
                                    "money": dic_baihu[name]["money"],
                                    "xyk_y": now_user_xyk,
                                    "xyk": dic_baihu[name]["xyk"],
                                    "xyk_time": time.time(),
                                    "logging_time": dic_baihu[name]["logging_time"]

                                }
                                dic_baihu.update(dic)
                                jieguo = db_file_write.db_write(dic_baihu)
                                print("正在支付中.....")
                                time.sleep(2)
                                if jieguo == True:
                                    logger.info("%s信用卡支付%s成功" % (name,sum_money2))
                                    logger1.info("%s信用卡支付%s成功" % (name, sum_money2))
                                    print("支付成功，即将返回上品列表")
                                    time.sleep(1)
                                    tag = False
                                else:
                                    logger.error("%s信用卡支付失败" % name)
                                    print("支付失败")
                            else:
                                tag=False
                elif choice3 == "3":
                    print("""
                             ------------------------------
                                    您目前余额为:%s
                                    您目前信用卡余额为:%s
                             ------------------------------
                                    """ % (user_yue, user_xyk))
                    while tag:
                        money_y = int(input("请输入你要使用多少余额: "))
                        time.sleep(1)
                        money_x = int(input("请输入你要使用多少信用卡: "))
                        time.sleep(1)
                        user_money_he = money_x + money_y
                        now_user_money = sum_money2 - user_money_he
                        if now_user_money < 0:
                            print("不足以支付,请重新输入要使用的钱数")
                            logger.error("%s信用卡和余额组合不足以支付" % name)
                            continue
                        else:
                            now_user_yue = int(dic_baihu[name]["money"]) - money_y
                            now_user_xyk = float(dic_baihu[name]["xyk_y"]) - money_x


                            while tag:
                                choice4 = input("确认输入Y/y,退出输入N/n: ")
                                if choice4 in ["y", "Y"]:
                                    dic[name] = {

                                        "pwd": dic_baihu[name]["pwd"],
                                        "money": now_user_yue,
                                        "xyk_y": now_user_xyk,
                                        "xyk": dic_baihu[name]["xyk"],
                                        "xyk_time": time.time(),
                                        "logging_time": dic_baihu[name]["logging_time"]
                                    }

                                    dic_baihu.update(dic)
                                    jieguo = db_file_write.db_write(dic_baihu)
                                    print("正在支付中.....")
                                    time.sleep(2)

                                    dic_baihu.update(dic)
                                    if jieguo == True:
                                        print("支付成功,即将返回商品列表")
                                        logger.info("%s组合支付%s成功" %(name,sum_money2))
                                        logger1.info("%s组合支付%s成功" % (name, sum_money2))
                                        tag = False
                                    else:
                                        logger.error("%s组合支付失败" % name)
                                        print("支付失败")
                                else:
                                    tag =False
                elif choice3 == "4":
                    logger.error("%s选择退出" % name)
                    tag = False
                else:
                    logger.error("%s输入错误" % name)
                    print("输入错误,请重新输入")
                    continue
    else:
        while tag:
            logger.info("%s购物车上品种为1" % (name))
            xyk_yue = int(dic_baihu[name]["money"]) + float(dic_baihu[name]["xyk_y"])
            user_yue = int(dic_baihu[name]["money"])
            user_xyk = float(dic_baihu[name]["xyk_y"])
            for i, v in shop_car.items():
                sum_money_shop = int(shop_car[i]["price"]) * \
                                 int(shop_car[i]["number"])

                l.append(i)
                s = " ".join([i, str(shop_car[i]["price"]),
                              str(shop_car[i]["number"]), str(sum_money_shop)])
                l.append(s)
                for i in range(len(l)):
                    if i % 2 != 0:
                        l1.append(l[i])
                    s4 = "\n".join(l1)
                if sum_money_shop > xyk_yue and sum_money_shop > user_xyk and \
                        sum_money_shop > user_yue:
                    logger.error("%s信用卡和余额不足以支付" % name)
                    print("您的余额和信用卡都不足以支付订单")
                    shop_car.clear()
                    return
                else:
                    print("""
    -------------清单---------------------
    商品名      单价    数量      总价
    %s



                                 共计:%s
    --------------------------------------
    """ % (s4, sum_money_shop))
                    time.sleep(1)
                    while tag:
                        print("""
                  ----------------------------------      
                        请选择支付方式
                        1.余额支付
                        2.信用卡支付
                        3.余额加信用卡组合支付
                        4.取消支付(系统会自动清空购物车)
                  -----------------------------------      
                        """)
                        choice3 = input("请选择: ")
                        if choice3 == "1":
                            if user_yue < sum_money_shop:
                                print("您目前余额为%s,不能支付请选择其他付款方式" % user_yue)
                                logger.error("%s余额支付不足" % name)
                                continue
                            else:
                                now_user_yue = user_yue - sum_money_shop
                                while tag:
                                    choice4 = input("确认输入Y/y,退出输入N/n: ")
                                    if choice4 in ["y", "Y"]:
                                        dic[name] = {

                                            "pwd": dic_baihu[name]["pwd"],
                                            "money": now_user_yue,
                                            "xyk_y": dic_baihu[name]["xyk_y"],
                                            "xyk": dic_baihu[name]["xyk"],
                                            "xyk_time": dic_baihu[name]["xyk_time"],
                                            "logging_time": dic_baihu[name]["logging_time"]
                                        }
                                        dic_baihu.update(dic)
                                        jieguo = db_file_write.db_write(dic_baihu)
                                        print("正在支付中.....")
                                        time.sleep(2)
                                        if jieguo == True:
                                            logger.info("%s余额支付%s成功" % (name,sum_money_shop))
                                            logger1.info("%s余额支付%s成功" % (name, sum_money_shop))
                                            print("支付成功,即将返回商品列表")
                                            time.sleep(1)
                                            tag = False
                                        else:
                                            logger.error("%s余额支付失败" % name)
                                            print("支付失败")
                                    elif choice4 in ["n", "N"]:
                                        tag = False
                                    else:
                                        logger.error("%s输入错误" % name)
                                        print("输入错误,请重新输入")
                                        continue
                        elif choice3 == "2":
                            if user_xyk < sum_money_shop:
                                logger.error("%s信用卡余额支付不足" % name)
                                print("您目前信用余额为%s,不能支付请选择其他付款方式" % user_xyk)
                                continue
                            else:
                                now_user_xyk = user_xyk - sum_money_shop

                                while tag:
                                    choice4 = input("确认输入Y/y,退出输入N/n: ")
                                    if choice4 in ["y", "Y"]:
                                        dic[name] = {

                                            "pwd": dic_baihu[name]["pwd"],
                                            "money": dic_baihu[name]["money"],
                                            "xyk_y": now_user_xyk,
                                            "xyk": dic_baihu[name]["xyk"],
                                            "xyk_time": time.time(),
                                            "logging_time": dic_baihu[name]["logging_time"]
                                        }
                                        dic_baihu.update(dic)

                                        jieguo = db_file_write.db_write(dic_baihu)
                                        print("正在支付中.....")
                                        time.sleep(2)
                                        if jieguo == True:
                                            print("支付成功,即将返回商品列表")
                                            time.sleep(1)
                                            logger.info("%s信用卡支付成功%s" % (name,sum_money_shop))
                                            logger1.info("%s信用卡支付成功%s" % (name, sum_money_shop))
                                            tag = False
                                        else:
                                            logger.error("%s信用卡支付失败" % name)
                                            print("支付失败")
                                    elif choice4 in ["n", "N"]:
                                        tag = False
                                    else:
                                        logger.error("%s输入错误" % name)
                                        print("输入错误,请重新输入")
                                        continue
                        elif choice3 == "3":
                            print("""
                        --------------------    
                            余额为:%s
                            信用卡余额为:%s
                        --------------------    
                            """ % (user_yue, user_xyk))
                            while tag:
                                money_y = int(input("请输入你要使用多少余额: "))
                                if money_y > user_yue:
                                    print("您输入的不对！")
                                    continue
                                money_x = int(input("请输入你要使用多少信用卡: "))
                                if money_x <0:
                                    print("您的信用卡可用额度不足")
                                user_money_he = money_x + money_y
                                now_user_money = sum_money_shop - user_money_he
                                if now_user_money > 0:
                                    logger.error("%s信用卡和余额组合不足以支付" % name)
                                    print("不足以支付,请重新输入要使用的钱数")
                                    continue
                                elif now_user_money == 0:
                                    now_user_yue = int(dic_baihu[name]["money"]) - money_y
                                    now_user_xyk = float(dic_baihu[name]["xyk"]) - money_x
                                    while tag:
                                        choice4 = input("确认输入Y/y,退出输入N/n: ")
                                        if choice4 in ["y", "Y"]:
                                            dic[name] = {

                                                "pwd": dic_baihu[name]["pwd"],
                                                "money": now_user_yue,
                                                "xyk_y": now_user_xyk,
                                                "xyk": dic_baihu[name]["xyk"],
                                                "xyk_time": time.time(),
                                                "logging_time": dic_baihu[name]["logging_time"]
                                            }
                                            dic_baihu.update(dic)

                                            jieguo = db_file_write.db_write(dic_baihu)
                                            print("正在支付中.....")
                                            time.sleep(2)
                                            if jieguo == True:
                                                print("支付成功,即将返回商品列表")
                                                time.sleep(1)
                                                logger.info("%s组合支付%s成功" % (name,sum_money_shop))
                                                logger1.info("%s组合支付%s成功" % (name, sum_money_shop))
                                                tag = False
                                            else:
                                                logger.error("%s组合支付失败" % name)
                                                print("支付失败")
                                        else:
                                            tag=False
                                else:
                                    print("您输入的金额不对，请重新核对账单后，在支付")
                                    time.sleep(1)
                        elif choice3 == "4":
                            logger.info("%s选择退出" % name)
                            tag = False
                        else:
                            logger.error("%s输入错误" % name)
                            print("输入错误,请重新输入")
                            continue