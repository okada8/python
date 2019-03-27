import os,sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core import admin_view,user_view


def start():
    func_dic = {"1": admin_view.views, "2": user_view.views}
    while True:
        print("""请选择界面
1.管理员
2.用户
q.退出""")
        res = input(">>>:").strip()
        if res == "q": exit(0)
        if res in func_dic:
            func_dic[res]()
        else:
            print("输入有误!")

if __name__ == '__main__':
    start()
