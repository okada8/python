from lib import common
from interface import student_interface
import os
logger = common.get_logging("student")
#学生选择学校
@common.auth
def choice_school(startname):
    # 如果学生之前已经选择了班级和课程，并且付了费用，那么他就不能选择学校了
    if common.name.classes and common.name.money == 1 and common.name.course:
        print("你已经选择课程，如果你已经学习完毕，请联系老师更改")
        return
    l = []
    #生成所有学校对象列表
    school_obj_lis = student_interface.student_choice_read("School")
    #学校列表为空
    if school_obj_lis == False:
        logger.error("%s选择的学校不存在"%common.name.name)
        print("对不起，学校暂未建成")
    count = 1
    #遍历每一个学校
    for i in school_obj_lis:
        #将学校信息重新组合成字符串
        sc_info = "【%s】%s %s %s" % (count, getattr(i, "name"), getattr(i, "address"), getattr(i, "tele"))
        #将字符串存入列表
        l.append(sc_info)
        count += 1
    #将列表每个元素用换行合并
    s = "\n".join(l)
    print("""
=======================================
      学校列表    具体地址    联系电话
%s   
=======================================
        """ % s)


    school_choice = int(input("请输入你要选择学校的编号：").strip())
    #选择学校对象
    choice_school = school_obj_lis[school_choice - 1]

    #该学生是否已经选择了该学校
    if common.name.school == choice_school.name:
        logger.error("%s选择的学校之前已经选择" % common.name.name)
        print("你已经选择该学校")
    else:
        #通过学生接口将学校和学生绑定到一起
        res = student_interface.student_attr_set(common.name, "school", choice_school)
        #如果返回结果不为空
        if not res:
            logger.info("%s选择了%s学校" % (common.name.name, choice_school.name))
            print("选择学校成功")
        logger.error("%s选择的学校失败" % common.name.name)
#学生选择课程
@common.auth
def choice_course(startname):
    # 如果学生学校不存在
    if not common.name.school:
        print("您还没有选择学校，请选择学校")
        return
    #每个学生只能选择一门课程
    if common.name.course:
        print("你已经有一门课程了，先学完再说")
        logger.error("%s已经有课程了" % common.name.name)
        return
    #获取该学生选择学校的学校对象
    sc_obj = student_interface.DB_handler.load_obj_from_file("school", common.name.school)
    #获取该学校的所以UK鄂城列表
    course_lis = sc_obj.course
    #获取课程字符串让学生选择
    c = "\n".join(course_lis)
    print("""
===你目前学校有以下课程====
%s
=======================    
    """ % c)
    while True:
        cou_choice = input("请输入你要选择的课程(q退出)：").strip()
        if cou_choice == "q":
            return
        if cou_choice not in course_lis:
            print("你输入的课程不存在")
            logger.error("%s选择的课程不存在" % common.name.name)
            continue
        if cou_choice in common.name.course:
            print("你已经选择了该课程，重新选择")
            logger.error("%s选择的课程已存在" % common.name.name)
            continue

        res = student_interface.student_attr_set(common.name, "course", cou_choice)
        if not res:
            print("加入课程成功")
            logger.info("%s选择了%s课程" % (common.name.name, cou_choice))
            return
        logger.error("%s加入课程失败" % common.name.name)
#学生选择班级
@common.auth
def choice_classes(startname):
    #如果学生学校为空
    if not common.name.school:
        print("你还没有选择学校和课程！")
        logger.error("%s选择的班级时，学校未选择" % common.name.name)
        return
    if common.name.classes:
        print("你已经选择过班级了，班级为%s校区的%s" % (common.name.school, common.name.classes))
        logger.error("%s选择的班级已存在" % common.name.name)
        return
    #获取学生对象的学校名字
    school_name = common.name.school
    #获取该学校对象
    school_obj = student_interface.DB_handler.load_obj_from_file("school", school_name)
    #获取该学校的班级列表
    class_lis = school_obj.classes
    if not class_lis:
        print("你所在学校还没有班级，请联系管理员创建")
    c = "\n".join(class_lis)
    print("""
======有以下班级可以选择=======
%s
============================    
    """ % c)
    while True:
        class_choice = input("请输入你要选择的班级(q退出):").strip()
        if class_choice == "q":
            return
        if class_choice not in class_lis:
            print("该班级不存在")
            logger.error("%s选择的班级不存在" % common.name.name)
            continue
        else:
            res = student_interface.student_attr_set(common.name, "classes", class_choice)
            if not res:
                logger.info("%s加入%s学校%s班级" % (common.name.name, school_name, class_choice))
                print("加入班级成功")
                return
            logger.error("%s加入%s班级失败" % (common.name.name,class_choice))
#查看成绩
@common.auth
def see_cou_grade(startname):
    print("""
=====你目前所学%s课程成绩如下======
%s
===============================    
    """ % (common.name.course, common.name.grade))

#学生交钱
@common.auth
def money(startname):
    #如果学生班级未选择
    if not common.name.classes:
        print("你还没有选择班级")
        logger.error("%s交钱时班级不存在" % common.name.name)
        return
    #该学生对象交过钱为1，未交钱为0
    if common.name.money == 1:
        print("你已经交过学费了")
        logger.error("%s交过学费了" % common.name.name)
        return
    #生成课程/学校目录
    floder_path=os.path.join("course",common.name.school)
    #获取课程对象
    course_obj = student_interface.DB_handler.load_obj_from_file(floder_path, common.name.course)

    print("""
=====请确认你的信息====
学校:{a}
班级:{b}            
课程:{c}         
周期:{d}           
费用:{e}
1.确认         2.退出
=====================
    """.format(a=common.name.school, b=common.name.classes, c=common.name.course, d=course_obj.time, e=course_obj.money))
    choice = input("请选择：")
    if choice == "1":
        while True:
            money_choice = input("请输入要缴费的金额：").strip()
            if money_choice.isdigit() == False:
                print("钱是数字")
                logger.error("%s输入交的钱不是数字" % common.name.name)
                continue
            if money_choice != course_obj.money:
                print("你付的钱不对")
                logger.error("%s输入交的钱不是课程费用" % common.name.name)
                continue
            #通过学生接口将学生的money变为1
            res = student_interface.student_attr_set(common.name, "money", 1)
            if not res:
                logger.info("%s交了%s" % (common.name.name, money_choice))
                print("缴费成功")
                return
            logger.error("%s交钱失败" % common.name.name)
    return


def main(start_name):
    fun_dic = {"1": common.register, "2": common.login, "3": choice_school,
               "4": choice_course, "5": choice_classes, "6": see_cou_grade, "7": money}
    while True:
        print("""
=======请选择对应功能===========    
        1.注册
        2.登录
        3.选择学校
        4.选择课程
        5.选择班级
        6.查看成绩
        7.学费缴纳
        8.退出
=============================    
        """)
        num = input("请输入你的选择：")
        if num == "8":
            return
        elif num in fun_dic:
            fun_dic[num](start_name)
        else:
            print("您输入错误，请重新输入!!!")
