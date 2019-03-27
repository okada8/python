from db.models import *
from db import DB_handler


# 该模块用于处理student注册数据
def student_resister(name, password):
    # 要判断是否存在这个学生
    filenames = DB_handler.get_all_filename(Student.__name__.lower())
    if not filenames:
        student = Student(name, password)
        DB_handler.save_obj_to_file(student)
        return student
    if name in filenames:
        return
    # 处理数据并且完成存储
    student = Student(name, password)
    DB_handler.save_obj_to_file(student)
    return student


# 该模块用于获取student选择学校，课程，老师的数据
def student_choice_read(obj_name):
    if obj_name == "School":
        obj_name = School
    elif obj_name == "Teacher":
        obj_name = Teacher
    else:
        obj_name = Course
    filenames = DB_handler.get_all_filename(obj_name.__name__.lower())
    if not filenames:
        return False
    # 生成对象
    obj_lis=[DB_handler.load_obj_from_file(obj_name.__name__.lower(), i)\
             for i in filenames]
    return obj_lis


# 该模块用于接收student选择学校，课程的数据
def student_attr_set(st_obj, name, choice_obj):
    if type(choice_obj) != str and type(choice_obj) != int:
        setattr(st_obj, name, choice_obj.name)
        DB_handler.save_obj_to_file(st_obj)
        return
    elif type(choice_obj) == str or type(choice_obj) == int:
          setattr(st_obj, name, choice_obj)
          DB_handler.save_obj_to_file(st_obj)
          return
    else:
        s = getattr(st_obj, name)
        s.append(choice_obj)
        DB_handler.save_obj_to_file(st_obj)
        return


if __name__ == '__main__':
    print(School.__name__)
