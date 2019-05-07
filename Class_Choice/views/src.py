from core import admin, student, teacher


def run():
    # 把编号当成key和方法名关联
    fun_dic = {"1": admin.main, "2": teacher.main, "3": student.main}
    while True:
        print("""
========欢迎使用选课系统，请选择角色===========
1.管理员
2.老师
3.学生
4.退出
==========================================       
        """)
        num = input("请做出选择: ").strip()
        if num == "4":
            break
        elif num in fun_dic:
# 因为管理员，老师，学生都需要登录，为了减少重复，在选择的时候得得到选择的是老师还是学生，还是管理员
            start_name = (fun_dic[num].__module__).split(".")[1]
            fun_dic[num](start_name)
        else:
            print("您输入的不正确!!!")


if __name__ == '__main__':
    run()
