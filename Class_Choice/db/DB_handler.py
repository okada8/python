import conf.settings as pt
import os
import pickle
import hashlib


# 将对象存储到文件中
def save_obj_to_file(*args):
    #对象是obj
    obj = args[0]
    #如果传进来参数为1个
    if len(args) == 1:
        # 文件夹路径是db+该对象的名字小写
        path = os.path.join(pt.DB_DIR, obj.__class__.__name__.lower())
        #写入文件只传入对象，路径
        write_obj_to_file(obj, path)
    else:
        #如果是2个，第一个是对象，。第二个是路径
        path = args[1]
        write_obj_to_file(obj, path)


def write_obj_to_file(obj, path):
    #如果传入的路径不存在，那么创建,是多级目录
    if not os.path.exists(path):
        os.makedirs(path)
    # 文件路径是传入的路径下面用对象的名字
    file_path = os.path.join(path, obj.name)
    # 写入文件
    with open(file_path, "wb") as f:
        pickle.dump(obj, f)
        f.flush()
        return


# 从目录中获取对象
def load_obj_from_file(floder_name, file_name):
    # 文件路径db+目录+文件名
    file_path = os.path.join(pt.DB_DIR, floder_name, file_name)
    # 判断路径是否存在
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            obj = pickle.load(f)
        #返回对象
        return obj


# 对密码进行加密
def halib_file(pwd):
    md_pwd = hashlib.md5()
    md_pwd.update(pwd.encode("utf-8"))
    return md_pwd.hexdigest()


# 用于从文件夹查找文件
def get_all_filename(dirname):
    #路径是db+目录名字
    dir_path = os.path.join(pt.DB_DIR, dirname)
    if os.path.exists(dir_path):
        #返回该目录下所有文件名的列表
        return os.listdir(dir_path)


if __name__ == '__main__':
    pass
    # obj = load_obj_from_file("teacher", "张三")
    # print(obj.__dict__)
    # a=os.path.split(os.path.abspath(r"D:\python\class_choice\db"))
    # print(a)