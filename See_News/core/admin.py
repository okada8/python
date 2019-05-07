from db import DB_handler
import time
from lib import common
logger=common.get_logging("admin")

def send_new(username):
    new_dic=DB_handler.get_news_read()
    dic={}
    while True:
        new_name=input("要添加的新闻名称: ").strip()
        if new_name in new_dic:
            print("新闻已经存在,请重新输入")
            logger.error("%s录入新闻时，新闻已存在"%username)
            continue
        else:
            new_text=input("要添加的新闻内容: ").strip()
            writer=input("作者是：").strip()
            dic[new_name]={
                "read_number": 0,
                "writer":writer,
                "time":time.strftime("%Y-%m-%d %X"),
                "text":new_text
            }
            new_dic.update(dic)
            res=DB_handler.get_news_write(new_dic)
            if res == True:
                print("新闻加入成功")
                logger.info("%s成功发布了新闻%s"%(username,new_name))
                return

def delet_new(username):
    new_dic = DB_handler.get_news_read()
    while True:
        new_name = input("要删除的新闻名称: ").strip()
        if new_name in new_dic:
            new_dic.pop(new_name)
            res=DB_handler.get_news_write(new_dic)
            if res == True:
                print("删除成功")
                logger.info("%s成功删除了新闻%s"%(username,new_name))
                return
        else:
            print("该新闻不存在")
            logger.error("%s删除的新闻不存在"%username)

def see_feed(username):
    cfg=DB_handler.myini_read()
    yijian=cfg.get(username,"yijian")
    s=yijian.split("-")
    print("""
==================================    
%s在%s对管理员说:
%s！！！   
==================================    
    """ %(s[0],s[2],s[1]))
    logger.info("%s查看了意见"%username)
    return

def lock_user(username):
    dic_user=DB_handler.get_user_read()
    while True:
        lock_name=input("请输入你要冻结谁: ")
        if lock_name in dic_user:
            for k in dic_user.keys():
                if k == lock_name:
                    dic_user[k]["lock"]=True
                    res=DB_handler.get_user_write(dic_user)
                    if res == True:
                        print("冻结成功")
                        logger.info("%s冻结了%s成功"%(username,k))
                        return
        else:
            print("该用户不存在")
            logger.error("%s冻结的账户不存在"%username)

def lock_open_user(username):
    dic_user = DB_handler.get_user_read()
    while True:
        lock_name=input("请输入你要解冻谁: ")
        if lock_name in dic_user:
            for k in dic_user.keys():
                if k == lock_name :
                    if dic_user[lock_name]["lock"] == True:
                        dic_user[k]["lock"]=False
                        res=DB_handler.get_user_write(dic_user)
                        if res == True:
                            print("解冻成功")
                            logger.info("%s解冻%s成功"%(username,k))
                            return
                    else:
                        print("该用户未冻结")
                        logger.error("%s解冻的账户未冻结"%username)
        else:
            print("该用户不存在")
            logger.error("%s解冻的账户不存在" % username)

def see_logger(username):
    while True:
        print("""
            1.管理员日志  
            2.用户日志
            3.返回
            """)
        choice = input("请选择: ")
        if choice == "1":
            f=DB_handler.admin_log_read()
            print(f)
            return
        elif choice == "2":
            f = DB_handler.user_log_read()
            print(f)
            return
        elif choice == "3":
            return
        else:
            print("输入错误")

def main(username):
    dic={"1":send_new,"2":delet_new,
         "3":see_feed,"4":lock_user,
         "5":lock_open_user,"6":see_logger}
    while True:
        print("""
    1.发布新闻
    2.删除新闻
    3.查看意见
    4.冻结账户
    5.解冻账户
    6.查看日志
    7.退出
    """)
        res = input("请输入编号: ").strip()
        if res in dic:
            dic[res](username)
        elif res == "7":
            return
        else:
            print("输入错误")
            break