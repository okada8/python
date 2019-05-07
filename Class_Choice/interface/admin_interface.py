from db.models import *
from db import DB_handler
from conf import settings
import os


# 该模块用于处理admin注册模块数据
def admin_resister(name, password):
    # 要判断是否存在这个管理员，返回管理员列表
    filenames = DB_handler.get_all_filename(Admin.__name__.lower())
    if not filenames:
        #生成管理员对象
        admin = Admin(name, password)
        DB_handler.save_obj_to_file(admin)
        return admin
    if name in filenames:
        return
    # 处理数据并且完成存储
    admin = Admin(name, password)
    DB_handler.save_obj_to_file(admin)


# 该模块用于处理admin创建学校模块数据
def admin_create_school(name, address, telephone):
    #获得学校列表
    filenames = DB_handler.get_all_filename(School.__name__.lower())
    if not filenames:
        #生成学习对象
        school = School(name, address, telephone)
        #保存学校对象
        DB_handler.save_obj_to_file(school)
        return school
    if name in filenames:
        return
    school = School(name, address, telephone)
    DB_handler.save_obj_to_file(school)
    return school


# 该模块用于处理admin创建课程数据
def admin_create_course(schol_name,course_name, course_time, course_money):
    #生成创建课程的路径，是不同学校可以创建相同课程
    filenames_path=os.path.join(settings.DB_DIR,Course.__name__.lower(),schol_name)
    #获得课程列表
    filenames = DB_handler.get_all_filename(filenames_path)
    if not filenames:
        #生成课程对象
        course = Course(course_name, course_time, course_money)
        DB_handler.save_obj_to_file(course,filenames_path)
        return
    if course_name in filenames:
        return course_name
    course = Course(course_name, course_time, course_money)
    DB_handler.save_obj_to_file(course,filenames_path)
    return


# 根据学校创建班级
def admin_create_classes(course_school, course_class):
    # 生成创建班级的路径，是不同学校可以创建相同班级
    file_path = os.path.join(settings.DB_DIR, Classes.__name__.lower(), course_school)
    filenames = DB_handler.get_all_filename(file_path)
    if not filenames:
        #生成班级对象
        classes = Classes(course_class)
        DB_handler.save_obj_to_file(classes, file_path)
        return
    if course_class in filenames:
        return course_class
    classes = Classes(course_class)
    DB_handler.save_obj_to_file(classes, file_path)
    return
