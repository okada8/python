from lib import common
from interface import teacher_interface
#生成日志生成器
logger = common.get_logging("teacher")

#查看该老师所交的课程
@common.auth
def see_tec_course(*args):
    #获取老师的所教课程列表
    tec_course = getattr(common.name, "course")
    if not tec_course:
        print("您目前没有任何校区的任何课程")
    else:
        s = "\n".join(tec_course)
        print("""
=======目前课程如下========
%s        
=========================        
        """ % s)

#老师选择课程
@common.auth
def cho_tec_course(*args):
    while True:
        #获取老师所在学校的学校对象
        sch_obj = teacher_interface.DB_handler.load_obj_from_file("school", common.name.school)
        #获取该学校的课程列表
        c = "\n".join(sch_obj.course)
        print("""
=======你所在校区有以下课程可选(q退出)=====
%s
======================================        
        """ % c)
        course1 = input("请选择课程：").strip()
        if course1 == "q":break
        if course1 in common.name.course:
            print("该校区课程你已经选择，请重新选择")
            logger.error("%s选择课程时，课程已经选择" % common.name.name)
            continue
        #获取该学校班级列表
        h = "\n".join(sch_obj.classes)
        print("""
=======你所选课程有以下班级可选=====
%s
================================        
                """ % h)
        t_class = input("请选择班级：").strip()
        if t_class in common.name.classes:
            print("你已经在该班级授课啦")
            logger.error("%s选择课程时，班级已经选择" % common.name.name)
            return
        #通过老师接口将老师名字，课程名字，班级名字更改
        res = teacher_interface.cho_tec_course(common.name, course1, t_class)
        if not res:
            print("你已经选择成功")
            logger.info("%s选择了%s课程%s班级" % (common.name.name, course1, t_class))
            return

#查看班级下面的学生
@common.auth
def see_cou_student(*args):
    #回去该老师的班级列表
    c = "\n".join(common.name.classes)
    print("""
====目前教以下几个班====
 %s   
=====================    
    """ % c)
    while True:
        choice = input("请输入你要看的班级(q退出):").strip()
        if choice == "q":
            break
        if choice not in common.name.classes:
            logger.error("%s查看班级下学生时，班级不存在" % common.name.name)
            print("该班级不存在")
            continue
        #获取所有学生列表，遍历学生列表，获取学生对象，将学生的姓名，成绩组成字符串并且加列表
        l_h=["%s %s" % (i, teacher_interface.DB_handler.load_obj_from_file("student", i).grade) \
             for i in teacher_interface.DB_handler.get_all_filename("student") \
             if teacher_interface.DB_handler.load_obj_from_file("student", i).school == common.name.school \
             and teacher_interface.DB_handler.load_obj_from_file("student", i).classes == choice]
        #将列表里字符串用换行拼接
        p = "\n".join(l_h)
        print("""
=====%s学员信息如下===
姓名 成绩
%s
=================        
        """ % (choice, p))
        return choice, teacher_interface.DB_handler.get_all_filename("student")

#更改学成绩
@common.auth
def set_stu_grade(*args):
    #先调用查看班级下学生方法得到班级名字和所有学生列表
    class_choice, st_file_lis = see_cou_student()
    st_name = input("要修改谁的成绩：").strip()
    #遍历学生列表
    for i in st_file_lis:
        #获取每个学生对象
        st_obj = teacher_interface.DB_handler.load_obj_from_file("student", i)
        #如果该学生的班级和你选择班级一样，学生姓名和你选择的姓名一样
        if st_obj.classes == class_choice and st_name == st_obj.name:
            while True:
                chengji = input("请输入成绩(q退出)：")
                if chengji == "q": break
                if chengji.isdigit():
                    #通过老师接口更改学生成绩
                    res = teacher_interface.set_tec_grade(st_obj, int(chengji))
                    if not res:
                        logger.info("%s把%s的成绩修改为%s" % (common.name.name, st_name, chengji))
                        print("你已经修改成功")
                        return
                else:
                    logger.error("%s更改学生成绩时，输入的成绩不是数字" % common.name.name)
                    print("成绩是数字！")
                    continue
        else:
            continue


def main(start_name):
    fun_dic = {"1": common.login, "2": see_tec_course, "3": cho_tec_course,
               "4": see_cou_student, "5": set_stu_grade}
    while True:
        print("""
=======请选择对应功能===========    
        1.登录 
        2.查看教授课程
        3.选择教授课程
        4.查看课程下学生
        5.修改学生成绩
        6.返回
=============================    
        """)
        num = input("请输入你的选择：")
        if num == "6":
            return
        elif num in fun_dic:
            fun_dic[num](start_name)
        else:
            print("您输入错误，请重新输入!!!")
