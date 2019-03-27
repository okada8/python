from db.models import *
from db import DB_handler


# 该方法用于处理teacher注册模块数据，在注册模块有被调用
def teacher_resister(name, password):
    # 要判断是否存在这个老师
    filenames = DB_handler.get_all_filename(Teacher.__name__.lower())
    school = input("请选择学校:").strip()
    #回去所有学校列表
    school_name = DB_handler.get_all_filename(School.__name__.lower())
    if school not in school_name:
        return "该学校不存在"
    # 第一次没有相对目录filenames为None
    if not filenames:
        #生成老师对象
        teacher = Teacher(name, password, school)
        DB_handler.save_obj_to_file(teacher)
        return
    if name in filenames:
        return "该老师已存在"
    # 处理数据并且完成存储
    teacher = Teacher(name, password, school)
    DB_handler.save_obj_to_file(teacher)
    return


# 该方法用于处理teacher选择课程数据
def cho_tec_course(obj, course1, t_class):
    #更改老师教课列表
    obj.course.append(course1)
    #更改老师教课班级
    obj.classes.append(t_class)
    DB_handler.save_obj_to_file(obj)
    return


# 该方法用于处理老师修改学生成绩
def set_tec_grade(st_obj, chengji):
    #将学生对象的成绩的值改为多少
    setattr(st_obj, "grade", chengji)
    DB_handler.save_obj_to_file(st_obj)
