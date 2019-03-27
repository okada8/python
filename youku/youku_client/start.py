import os,sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core import admin,user

if __name__ == '__main__':
    funcs = {"1": admin.admin_view, "2": user.user_view}
    while True:
        print("""
    1.管理员界面
    2.用户界面
    """)
        res = input("请选择:>>>")
        if res == "q":
            break
        if res in funcs:
            funcs[res]()
        else:
            print("输入不正确!")