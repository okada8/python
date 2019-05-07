# 存储配置信息
import os

# 项目根路径
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# 数据文件路径
DB_DIR = os.path.join(BASE_DIR, "db")
STUDENT_LOG = os.path.join(BASE_DIR, "log", "Student.log")
ADMIN_LOG = os.path.join(BASE_DIR, "log", "Admin.log")
TEACHER_LOG = os.path.join(BASE_DIR, "log", "Teacher.log")
