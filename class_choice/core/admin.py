from lib import common
from interface import admin_interface
#生成日志生成器
logger = common.get_logging("admin")


# 创建学校
@common.auth
def create_school(*args):
    while True:
        name = input("请输入学校名(q退出)").strip()
        if name == "q": break
        if not name:
            print("学校的名字不能为空")
            logger.error("%s输入学校为空"%common.name.name)
            continue
        address = input("请输入学校地址:").strip()
        if not address:
            print("学校地址不能为空")
            logger.error("%s输入学校地址为空"%common.name.name)
            continue
        telephone = input("请输入学校电话:").strip()
        if not telephone:
            print("电话不能为空")
            logger.error("%s输入学校电话为空" % common.name.name)
            continue
        if telephone.isdigit() == False:
            print("电话为数字")
            logger.error("%s输入学校电话不是数字" % common.name.name)
            continue
        #将学校的信息传给管理员接口层
        obj = admin_interface.admin_create_school(name, address, telephone)
        if obj:
            print("学校创建成功")
            logger.info("%s创建了%s学校" % (common.name.name, name))
            return
        else:
            logger.error("%s输入学校是存在的" % common.name.name)
            print("学校已存在")


# 创建老师
@common.auth
def create_teacher(*args):
    #创建老师就是调用注册接口，然后返回老师的名字
    username = common.register("teacher")
    logger.info("%s创建了%s老师" % (common.name.name, username))


# 创建课程，将课程绑定到学校，班级
@common.auth
def create_course(*args):
    while True:
        course_name = input("请输入课程(q退出)").strip()
        if course_name == "q": break
        if not course_name:
            print("课程名字不能为空")
            logger.error("%s输入课程名字为空" % common.name.name)
            continue
        if course_name.isdigit():
            print("课程输入错误")
            logger.error("%s输入课程名字是数字" % common.name.name)
            continue
        course_time = input("请输入课程周期:").strip()
        if not course_time:
            print("课程周期不能为空")
            logger.error("%s输入课程周期为空" % common.name.name)
            continue
        course_money = input("请输入课程费用:").strip()
        if not course_money:
            print("课程费用不能为空")
            logger.error("%s输入课程费用为空" % common.name.name)
            continue
        if course_money.isdigit() == False:
            print("课程费用为数字")
            logger.error("%s输入课程费用不是数字" % common.name.name)
            continue
        course_school = input("请输入在哪个学校：").strip()
        if not course_school:
            print("校名不为空")
            logger.error("%s将课程加入学校时输入学校为空" % common.name.name)
            continue
        if course_school.isdigit():
            print("校名输入错误")
            logger.error("%s将课程加入学校时输入是数字" % common.name.name)
            continue
        #获取相对应的学校对象
        sc_obj = admin_interface.DB_handler.load_obj_from_file("school", course_school)
        #判断该学校课程是否存在该课程
        if course_name in getattr(sc_obj, "course"):
            print("该学校有这个课程了")
            logger.error("%s往%s添加%s课程是重复" %(common.name.name,course_school,course_name))
            return
        #否则学校对象的课程列表将该课程加入
        sc_obj.course.append(course_name)
        #为学校创建班级
        course_class = input("请输入班级名称：").strip()
        # 为学校创创建班级
        sc_obj.classes.append(course_class)
        #创建班级对象
        class_obj = admin_interface.admin_create_classes(course_school, course_class)
        #通过admin接口保存学校对象
        obj1 = admin_interface.DB_handler.save_obj_to_file(sc_obj)
        #通过接口层创建课程
        obj=admin_interface.admin_create_course(course_school,course_name, course_time, course_money)
        #所有返回值都不为空，说明课程创建成功
        if not obj1 and not class_obj and not obj:
            print("课程创建成功")
            logger.info("%s创建了%s课程%s班级" % (common.name.name, course_name, course_class))
            return
        else:
            logger.error("%s创建%s课程%s班级时课程已存在" % (common.name.name, course_name, course_class))
            print("课程已存在")


# 入口函数
def main(start_name):
    fun_dic = {"1": common.login, "2": common.register, "3": create_school,
               "4": create_teacher,"5":create_course}
    while True:
        print("""
=======请选择对应功能===========    
    1.登录
    2.注册
    3.创建学校
    4.创建老师
    5.创建课程
    6.返回
=============================    
    """)
        num = input("请输入你的选择：").strip()
        if num == "6":
            return
        elif num in fun_dic:
            fun_dic[num](start_name)
        else:
            print("您输入错误，请重新输入!!!")
