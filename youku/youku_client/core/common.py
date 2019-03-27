from Tcpclient import Tcpclient

def login(user_type=0):
    while True:
        name = input("name:")
        if name == "q":
            break
        password = input("password:")
        if name and password:
            data = {"name": name,
                    "password": password,
                    "type": "common",
                    "user_type": user_type,
                    "method":"login"}
            response = Tcpclient.request(data)
            if response["status"] == "ok":
                print("登录成功")
                return response
            else:
                print(response["msg"])
        else:
            print("输入有误!")

def register(user_type=0):
    while True:
        name = input("name:")
        if name == "q":
            break
        password = input("password:")
        if name and password:
            data = {"name": name,
                    "password": password,
                    "type":"common",
                    "user_type":user_type,
                    "method": "register",
                    }
            response = Tcpclient.request(data)

            if response["status"] == "ok":
                print("注册成功")
                break
            else:
                print(response["msg"])
        else:
            print("输入有误!")