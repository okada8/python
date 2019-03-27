from db import DB_handler
import time
import re
from lib import common
logger=common.get_logging("user")

def show_news(*args):
   while True:
        l_name = []
        dic_news = DB_handler.get_news_read()
        title=list(dic_news.keys())
        res=sorted(title,key=lambda k:dic_news[k]["read_number"],reverse=True)
        for i in res:
            l_name.append(i)
        q = "\n".join(l_name)
        print("""
============================
        今日新闻如下
%s
                    
============================""" %q)
        choice=input("请选择你要看的新闻的标题q退出：").strip()
        if choice in l_name:
            content = "\n".join(re.findall(".{1,28}", dic_news[choice]["text"]))
            print("""
=============================================================            
     【{a}】          
{b}
【作者】{d}
【浏览量】{e}
【发表时间】{c}
【1】:收藏                 【2】:返回           
===============================================================            
            """.format(a=choice,c=dic_news[choice]["time"],
                       b=content,
                       d=dic_news[choice]["writer"],
                       e=dic_news[choice]["read_number"]))
            dic_news[choice]["read_number"]+=1
            DB_handler.get_news_write(dic_news)
            choice1=input("请选择：")
            if choice1 == "1":
                add_collection(choice,*args)
            else:
                continue
        elif choice == "q":
            return
        else:
            print("输入不正确")

def search_news(username):
    dic_news=DB_handler.get_news_read()
    new_name=[]
    new_txt=[]
    l=[]
    neirong = input("请输入你要搜索的关键字：").strip()
    for n,v in dic_news.items():
        new_name.append(n)
        new_txt.append(v["text"])
    for n  in range(len(new_name)):
        line1=re.findall(neirong,new_txt[n])
        if line1 !=[]:
            content = "\n".join(re.findall(".{1,28}",new_txt[n]))
            s="【%s】\n\n%s" %(new_name[n],content)
            l.append(s)
    new = "\n\n".join(l)
    print("搜索中..........")
    time.sleep(2)
    print("""
================================================
            搜索到以下新闻

%s

================================================    
        """ % new)
    logger.info("%s搜索了新闻"%username)
    return True

def feedback(username):
    dic_user=DB_handler.get_user_read()
    cfg=DB_handler.myini_read()
    l_g = []
    l_h = []
    yijain1 = input("请提出宝贵的意见：")
    for k, v in dic_user.items():
        if v["type"] == 1:
            l_g.append(k)
    for name in l_g:
        s = "%s-%s-%s" % (username, yijain1,time.strftime("%Y%m%d %X"))
        l_h.append(s)
        cfg.set(name, "yijian", s)
        res=DB_handler.myini_write(cfg)
        if res == True:
            print("意见提交成功")
            logger.info("%s提交了意见%s"%(username,yijain1))
            return True

def delet_news(username,delet_new_name,cfg,res):
    res.remove(delet_new_name)
    g="|".join(res)
    cfg.set(username,"shoucang",g)
    res=DB_handler.myini_write(cfg)
    if res == True:
        print("删除成功")
        logger.info("%s删除了收藏%s"%(username,delet_new_name))
    return

@common.yanzheng
def add_collection(news_name,username):
    res = DB_handler.collection_write(username,news_name)
    if res == True:
        time.sleep(1)
        logger.info("%s收藏了新闻%s" %(username,news_name))
        print("收藏成功")

def my_collection(username):
    while True:
        cfg, res = DB_handler.collection_read(username)
        q = "\n".join(res)
        print("""
==============================
        我的收藏%s
    
1：删除                2.返回
==============================
        """ %q)
        choice=input("请选择：").strip()
        logger.info("%s查看了收藏夹" %username)
        if choice == "1":
            delet_new_name=input("请输入要删除的新闻名字：").strip()
            if delet_new_name in res:
                delet_news(username,delet_new_name,cfg,res)
            else:
                print("输入错误，请重新输入")
                continue
        elif choice == "2":
            return
        else:
            print("你输入错误")

def main(username):
    dic={"1":show_news,"2":search_news,"3":feedback,"4":my_collection}
    while True:
        print("""
        1.查看新闻
        2.搜索新闻
        3.问题反馈
        4.我的收藏
        5.退出
        """)
        res = input("请输入编号: ").strip()
        if res in dic:
            dic[res](username)
        elif res == "4":
            return
        else:
            print("输入错误")
            break

if __name__ == '__main__':
    search_news("apple")