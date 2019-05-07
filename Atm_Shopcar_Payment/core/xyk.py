from db import db_file_write
from lib import log_user
import time,os
Path1=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
log1=r"atm_shopcar_payment\log\信用卡业务.log"
log2=r"atm_shopcar_payment\log\流水.log"
Logpath=os.path.join(Path1,log1)
Logpath1=os.path.join(Path1,log2)
logger=log_user.getlog(Logpath,"xyk")
logger1 = log_user.getlog(Logpath1, "xyk2")

tag=True
dic_bai1={}
def xyk_ye1(name,*args):
    global tag

    dic_bai=args[0]
    tag=True
    dic={"1":huankuan,"2":quxian}
    if time.strftime("%d") == "22":
        logger.info("%s打印22日账单"%name)

        xyk_q=float(dic_bai[name]["xyk"])-float(dic_bai[name]["xyk_y"])

        print("""
        今天是{a}
        您的信用卡欠款为：{b}
        您的信用卡可用余额为：{c}
        请在每个月10号当天或当天之前按时还款!!!
        """.format(a=time.strftime("%Y-%m-%d"),b=xyk_q,c=dic_bai[name]["xyk_y"]))

    while tag:

            print("""
        --------------    
            1.还款
            2.取现
            3.退出
        --------------    
        """)
            choice=input("请输入你要办的信用卡业务:")
            if choice in dic:
                dic[choice](name,dic_bai)
                logger.info("%s选择了信用卡业务%s" %(name,dic[choice]))
            elif choice == "3":
                tag = False
                logger.info("%s选择了退出" % name)
            else:
                logger.error("%s输入有误" % name)
                print("输入错误")
                continue


def huankuan(name,dic_bai):
    global tag
    xyk_q = float(dic_bai[name]["xyk"]) - float(dic_bai[name]["xyk_y"])
    if time.strftime("%d") > "10":
        xyk_q1 = float(dic_bai[name]["xyk"]) - float(dic_bai[name]["xyk_y"])
        logger.info("%s为10号之后还款"%name)
        qikuantianshu=(float(time.time())-float(dic_bai[name]["xyk_time"]))//86400
        for i in range(1,int(qikuantianshu)):
            count=xyk_q*0.0005
            xyk_q1+=count
        xyk_q2=int(xyk_q1)
        print("""
    ------------------------    
        欠款为%s
        欠款%s天
        需还款%s
    ------------------------    
        """ %(xyk_q,qikuantianshu,int(xyk_q2)))
        money2=input("请输入还款金额：")
        if money2.isdigit():

            if int(money2) <= xyk_q2:
                if int(money2) < xyk_q2:
                    dic_bai1.clear()
                    dic_bai1[name]={
                        "pwd": dic_bai[name]["pwd"],
                        "money": dic_bai[name]["money"],
                        "xyk_y": money2,
                        "xyk": dic_bai[name]["xyk"],
                        "xyk_time": time.time(),
                        "logging_time": dic_bai[name]["logging_time"]
                    }
                    dic_bai.update(dic_bai1)
                    jieguo1=db_file_write.db_write(dic_bai)
                    if jieguo1 == True:
                        print("还款成功")
                        logger1.info("%s还款%s成功" % (name, money2))
                        logger.info("%s还款%s成功" %(name,money2))
                        tag = False
                    else:
                        print("还款失败")
                        logger.error("%s还款%s失败" % (name, money2))
                elif int(money2) == xyk_q2:
                    dic_bai1.clear()
                    dic_bai1[name] = {
                        "pwd": dic_bai[name]["pwd"],
                        "money": dic_bai[name]["money"],
                        "xyk_y": dic_bai[name]["xyk"],
                        "xyk": dic_bai[name]["xyk"],
                        "xyk_time": "0",
                        "logging_time": dic_bai[name]["logging_time"]
                    }
                    dic_bai.update(dic_bai1)
                    jieguo3 = db_file_write.db_write(dic_bai)
                    if jieguo3 == True:
                        print("还款成功")
                        logger1.info("%s还款%s成功" % (name, money2))
                        logger.info("%s还款%s成功" % (name, money2))
                        tag = False
                    else:
                        print("还款失败")
                        logger.error("%s还款%s失败" % (name, money2))
            else:
                print("还款不对")
                logger.error("%s还款数为%s大于欠款" %(name,money2))
        else:
            print("输入错误")
            logger.error("%s还款输入错误" %name)

    else:
        logger.info("%s为10号之前还款"%name)
        while tag:
            money=input("请输入还款金额：")
            if money.isdigit():
                xinyongky=int(money)+int(dic_bai[name]["xyk_y"])
                if xinyongky <= int(dic_bai[name]["xyk"]):
                    if xinyongky <int(dic_bai[name]["xyk"]):
                        dic_bai1.clear()
                        dic_bai1[name]={
                            "pwd": dic_bai[name]["pwd"],
                            "money": dic_bai[name]["money"],
                            "xyk_y": str(xinyongky),
                            "xyk": dic_bai[name]["xyk"],
                            "xyk_time": time.time(),
                            "logging_time": dic_bai[name]["logging_time"]
                        }
                        dic_bai.update(dic_bai1)
                        jieguo=db_file_write.db_write(dic_bai)
                        if jieguo == True:
                            print("还款成功")
                            logger1.info("%s还款%s成功" % (name, money))
                            logger.info("%s还款%s成功" %(name,money))
                        else:
                            print("还款失败")
                            logger.info("%s还款%s失败" % (name, money))
                    elif xinyongky == int(dic_bai[name]["xyk"]):
                        dic_bai1.clear()
                        dic_bai1[name] = {
                            "pwd": dic_bai[name]["pwd"],
                            "money": dic_bai[name]["money"],
                            "xyk_y": str(xinyongky),
                            "xyk": dic_bai[name]["xyk"],
                            "xyk_time": "0",
                            "logging_time": dic_bai[name]["logging_time"]
                        }
                        dic_bai.update(dic_bai1)
                        jieguo = db_file_write.db_write(dic_bai)
                        if jieguo == True:
                            print("还款成功")
                            logger.info("%s全额还款%s成功" % (name, money))
                            logger1.info("%s全额还款%s成功" % (name, money))
                        else:
                            print("还款失败")
                            logger.info("%s全额还款%s失败" % (name, money))
                else:
                    print("您输入的还款金额不对")
                    logger.error("%s还款为%s,大于信用卡总额度" %(name,xinyongky))
            else:
                print("请输入数字")
                logger.error("%s还款时输入错误" %(name))
                continue
def quxian(name,dic_bai):
    global tag
    while tag:
        money=input("请输入你要取多少,会收取%5的手续费：")
        if money.isdigit():
             xinyongkayue=dic_bai[name]["xyk_y"]
             xinyongkazonge=dic_bai[name]["xyk"]
             if float(money)+float(money)*0.05 < float(xinyongkayue):
                 while tag:
                    print("""
                 --------------    
                     1.确定
                     2.退出
                 --------------    
                    """)
                    choice1=input("确认按1，退出按2:")
                    if  choice1 == "1":
                        now_xyk_y=float(xinyongkayue)-(float(money)*0.05)-float(money)
                        dic_bai1[name]={
                            "pwd": dic_bai[name]["pwd"],
                            "money": dic_bai[name]["money"],
                            "xyk_y":str(now_xyk_y),
                            "xyk": dic_bai[name]["xyk"],
                            "xyk_time": time.time(),
                            "logging_time": dic_bai[name]["logging_time"]
                            }
                        dic_bai.update(dic_bai1)
                        jieguo=db_file_write.db_write(dic_bai)
                        if jieguo ==True:
                            print("正在吐钞中.....")
                            time.sleep(2)
                            print("""
                    -------------------------       
                            取现成功！！！
                            信用卡余额：%s
                            取出额度：%s
                            信用卡总额：%s
                    --------------------------        
                            """ %(now_xyk_y,float(money),xinyongkazonge))
                            time.sleep(1)
                            logger.info("%s信用卡取现%s" %(name,int(money)))
                            logger1.info("%s信用卡取现%s" % (name, int(money)))
                            tag =False
                        else:
                            logger.error("%s信用卡取现%s失败" %(name,int(money)))
                            print("取款失败")
                    elif choice1 == "2":
                        tag = False
                        logger.info("%s选择了退出" %name)
                    else:
                        print("输入错误")
                        logger.error("%s输入错误")
             else:
                 logger.error("%s信用卡取现余额不足" %name)
                 print("信用卡余额不足")
        else:
            logger.error("%s信用卡业务输入有误")
            print("请输入数字")
            continue




