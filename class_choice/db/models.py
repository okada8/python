# 基类
class Baseclass:
    def __init__(self, name, pwd):
        self.name = name
        self.pwd = pwd


# 课程类
class Course():
    def __init__(self, name, time, money):
        self.name = name
        self.time = time
        self.money = money


class Classes:
    def __init__(self, name):
        self.name = name


# 学校类
class School():
    def __init__(self, name, address, tele):
        self.name = name
        self.address = address
        self.tele = tele
        self.course = []
        self.classes = []


# 管理员类
class Admin(Baseclass):
    def __init__(self, name, pwd):
        super().__init__(name, pwd)


# 老师类
class Teacher(Baseclass):
    def __init__(self, name, pwd, school):
        super().__init__(name, pwd)
        self.school = school
        self.course = []
        self.classes = []


# 学生类
class Student(Baseclass):
    def __init__(self, name, pwd):
        super().__init__(name, pwd)
        self.classes = ""
        self.school = ""
        self.course = ""
        self.grade = 0
        self.money = 0


if __name__ == '__main__':
    pass
