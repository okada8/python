import os


def create_home_dir(name):
    """
    创建用户的home目录
    :return:
    """
    if not os.path.exists("root"): #先创建root目录
        os.makedirs("root")

    # 判断是否存在
    home_path = os.path.join("root",name)
    if not os.path.exists(home_path):
        os.makedirs(home_path)

