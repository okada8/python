import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from lib import common
from core import admin,user
from db import DB_handler
logger1=common.get_logging("admin")

def run():
    while True:
        print("""
***********************************
         欢迎来到新闻浏览器        
1.查看新闻              
2.登录
3.注册
4.退出
***********************************    
        """)
        choice=input("请输入你的选择：").strip()
        if choice == "1":
            user.show_news()
        elif choice == "2":
            jieguo,username=common.logginger()
            if jieguo == 1:
                admin.main(username)
                logger1.info("%s登陆成功"%username)
            elif jieguo == 0:
                user.main(username)
                common.logger2.info("%s登陆成功"%username)
        elif choice == "3":
            dic_user = DB_handler.get_user_read()
            common.zhuce(dic_user)
        elif choice == "4":
            exit(0)
        else:
            print("您输入的不正确，请重新输入！！！")

if __name__ == '__main__':
    run()