import hashlib
import os
import re
def getMD5(path):
    md5 = hashlib.md5()
    with open(path,"rb") as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            md5.update(data)

    return md5.hexdigest()


# 判断本地是否存在一个文件
def exists_file(filename,username):
    # 是否存在该路径
    if not os.path.exists("data"):
        os.makedirs("data")

    # 创建用户文件夹
    home = os.path.join("data",username)
    if not os.path.exists(home):
        os.makedirs(home)

    path = os.path.join("data",username,filename)
    return os.path.exists(path)


# 如果文件已经存在 则根据已经存在的名称 造一个新的名字
def get_new_filename(name):
    # name 使用户自己输入的 绝壁没括号

    if "(" in name:
        # test.txt  (1)
        res = int(re.findall("\((\d)\)",name)[0])
        res += 1
        name += str(res)
        print(res)
    else:
        name += "(1)"
    return name


if __name__ == '__main__':
    # print(getMD5(r"D:\python6期视频\并发作业\FTP\client\md5_tool.py"))
    print(get_new_filename("test.txt(1)"))





