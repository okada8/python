import sys,os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import socket,pymysql,select,struct,json
dic={}

def DB(dic,i):
    dic1={}
    try:
        conne = pymysql.connect(host=dic[i]["host"], port=int(dic[i]["port"]), user=dic[i]["user"],passwd=dic[i]["pwd"], database=dic[i]["db"])
        course = conne.cursor()
        course.execute(dic[i]["sql"])
        data = course.fetchall()
        dic1["res"]=data
        dic2=json.dumps(dic1)
        course.close()
        conne.close()
    except Exception as e:
        dic1["res"] = str(e)
        dic2 = json.dumps(dic1)
        return dic2
    return dic2

def app():
    global dic
    c=socket.socket()
    c.bind(("127.0.0.1",8888))
    c.listen()
    r_list=[c]
    w_list=[]
    while True:
        read,write,_=select.select(r_list,w_list,[])
        for i in read[:]:
            if i == c:
                s,_=i.accept()
                r_list.append(s)
            else:
                try:
                        s1=i.recv(8)
                        if not s1:
                            i.close()
                            r_list.remove(i)
                            continue
                        s2s=struct.unpack("q",s1)[0]
                        s2=i.recv(s2s)
                        if not s2:
                            i.close()
                            r_list.remove(i)
                        dic1=json.loads(s2)
                        w_list.append(i)
                        dic[i]=dic1
                except ConnectionResetError as e:
                    print(e)
                    i.close()
                    r_list.remove(i)
        for i in w_list[:]:
            data1=DB(dic,i)
            try:
                data_len=struct.pack("q",len(data1))
                i.send(data_len)
                i.send(data1.encode("utf-8"))
            except ConnectionResetError as e:
                print(e)
                i.close()
            finally:
                w_list.remove(i)
                dic.pop(i)
if __name__ == '__main__':
    app()






























