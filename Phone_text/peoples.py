

import pickle

class People(object):

    def __init__(self,name,work,phone,email):
        self.name=name
        self.work=work
        self.phone=phone
        self.email=email

    # 删除某个信息
    def dele(self):
            while True:
                text = input("1:确认删除,2:返回上一级：").strip()
                if not text:
                    continue
                if text == "1":
                    r_l=opens()
                    r_l.pop(r_l.count(self))
                    if not writes(r_l):
                        return "删除成功"
                elif text == "2":
                    return
                else:
                    continue


    #修改某个信息
    def edit(self):
        peop_list = opens()
        n_l = [p_name.name for p_name in peop_list]
        w_l = [p_name.work for p_name in peop_list]
        t_l = [p_name.phone for p_name in peop_list]
        e_l = [p_name.email for p_name in peop_list]
        peop_list.pop(peop_list.count(self))
        while True:
            text=input("""
请输入修改项
1.姓名
2.电话
3.工作地址
4.邮箱
选择：
            """).strip()
            if text not in ["1","2","3","4"]:
                print("输入错误返回上一级")
                return
            if text == "1":
                name1=input("请输入新的姓名:").strip()
                if not name1 or name1 in n_l:
                    print("姓名输入错误！")
                    continue
                self.name=name1
                break
            elif text == "2":
                phone1 = input("请输入新的电话: ").strip()
                if not phone1 or not phone1.isdigit() or len(phone1) != 11 or phone1 in t_l:
                    print("电话输入错误！")
                    continue
                self.phone=phone1
                break
            elif text == "3":
                work1=input("请输入新的工作地址：").strip()
                if not work1 or work1 in w_l:
                    print("工作地址输入错误")
                    continue
                self.work=work1
                break
            else:
                email1=input("请输入新的邮箱：").strip()
                if not email1 or email1 in e_l:
                    print("邮箱输入错误")
                    continue
                self.email=email1
                break
        peop_list.append(self)
        if not writes(peop_list):
            return "更新成功"


    #查看某个人信息
    def show(self):
        s1 = "%s   \t%s   %s       %s\n" % (self.name, self.phone, self.email, self.work)
        print(
            """
*****************************************************            
姓名          电话            邮箱           工作地点              
%s


       1:【删除】     2:【修改】    3:【返回】  
*****************************************************
            """
            % (s1))
        while True:
            choice = input("请选择: ").strip()
            if choice not in ["1","2",'3']:
                continue
            if choice == "1":
                print(self.dele())
                return
            elif choice == "2":
                print(self.edit())
                return
            else:
                return

#增加
def add():
    l=[]
    peop_list = opens()
    if peop_list:
        n_l=[p_name.name for p_name in peop_list]
        w_l=[p_name.work for p_name in peop_list]
        t_l=[p_name.phone for p_name in peop_list]
        e_l=[p_name.email for p_name in peop_list]
        while True:
            name = input("请输入姓名:").strip()
            if not name or name in n_l:continue
            work = input("请输入工作地址：").strip()
            if not work or work in w_l:continue
            phone = input("请输入电话: ").strip()
            if not phone or not phone.isdigit() or len(phone) != 11 or phone in t_l:continue
            email = input("请输入邮件：").strip()
            if not email or email in e_l:continue
            p1 = People(name, work, phone, email)
            peop_list.append(p1)
            if not writes(peop_list):
                return "存入通讯录成功"
    while True:
        name = input("请输入姓名:").strip()
        if not name : continue
        work = input("请输入工作地址：").strip()
        if not work : continue
        phone = input("请输入电话: ").strip()
        if not phone or not phone.isdigit() or len(phone) != 11: continue
        email = input("请输入邮件：").strip()
        if not email : continue
        p1 = People(name, work, phone, email)
        l.append(p1)
        if not writes(l):
            return "存入通讯录成功"

# 打开文件读取内容
def opens():
    try:
        with open("a.txt","rb") as line:
            f=line.read()
            return pickle.loads(f)
    except Exception:
        return False

#打开文件写入内容
def writes(obj_l):
    try:
        pic_obj=pickle.dumps(obj_l)
        with open('a.txt','wb') as line:
            line.write(pic_obj)
    except Exception:
        return False

#展示所有保存信息
def shows():
    peop_list=opens()

    if not peop_list:
        print( "通讯录为空")
        return
    g=""
    for ps in peop_list:
        s1="%s   \t%s   %s       %s\n"%(ps.name,ps.phone,ps.email,ps.work)
        g+=s1
        print(
            """
姓名          电话            邮箱           工作地点              
%s
            
            """
            % (g))

#查找信息
def find():
    peop_list = opens()
    if not peop_list:
        print("通讯录为空")
        return
    text = input("请输入电话或者姓名：").strip()
    for p in peop_list:
        if p.name == text or p.phone == text:
            p.show()
        else:
            print("没有该联系人")

#入口函数
def main():
    while True:
        print(
            """
*************通讯录管路系统*************        

            1.查看所有记录
            2.查找记录(修改，删除)
            3.添加记录
                            【4 退出】
**************************************
            """
        )
        choice = input("输入对应编号：").strip()

        if choice == "1":
            shows()
        elif choice == "2":
            find()
        elif choice == "3":
            print(add())
        elif choice == "4":
            break
        else:
            print("输入不正确")

if __name__ == '__main__':
    main()



