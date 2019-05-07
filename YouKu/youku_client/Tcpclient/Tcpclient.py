import socket
import json
import struct

conn=None

def connect():
    global conn
    conn=socket.socket()
    conn.connect(("127.0.0.1",9998))


def request(data):
    if not conn:
        try:
            connect()
        except Exception as e:
            print(e)
            exit(0)
    json_data=json.dumps(data).encode("utf-8")
    len_data=struct.pack("q",len(json_data))
    try:
        conn.send(len_data)
        conn.send(json_data)
        len_data=conn.recv(8)
        length=struct.unpack("q",len_data)[0]
        json_data=conn.recv(length).decode("utf-8")
        dic=json.loads(json_data)
        return dic
    except ConnectionResetError as e:
        print(e)
        conn.close()
        exit(0)

if __name__ == '__main__':
    connect()