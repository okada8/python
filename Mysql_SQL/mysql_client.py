import sys,os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import socket,struct,json,time
dic1={}

def logger():
    global dic1
    while True:
        server = input("数据服务器：").strip()
        if not server: continue
        time.sleep(0.2)
        port = input("数据库端口:").strip()
        if not port: continue
        time.sleep(0.2)
        user = input("数据库登录用户:").strip()
        if not user: continue
        time.sleep(0.2)
        pwd = input("数据库请输入密码:").strip()
        if not pwd: continue
        time.sleep(0.2)
        dic = {"host": server, "port": port, "user": user, "pwd": pwd}
        return dic

def app():
    global dic1
    c=socket.socket()
    c.connect(("127.0.0.1",8888))
    while True:
        if not dic1:
            dic2=logger()
            dic1.update(dic2)
        db=input("你要操作哪个库:").strip()
        if not db:continue
        time.sleep(0.2)
        sql=input("你要执行的sql:").strip()
        if not sql:continue
        time.sleep(0.2)
        dic4={"sql":sql,"db":db}
        dic1.update(dic4)
        dic1_js = json.dumps(dic1)
        dic1_len=struct.pack("q",len(dic1_js))
        c.send(dic1_len)
        c.send(dic1_js.encode("utf-8"))
        data=c.recv(8)
        res_js=struct.unpack("q",data)[0]
        res=c.recv(res_js)
        if "1045" in json.loads(res)["res"] or "invalid" in json.loads(res)["res"] :
            dic1.clear()
            logger()
        print(json.loads(res)["res"])

if __name__ == '__main__':
    app()
