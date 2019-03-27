import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# print(os.path.dirname(os.path.dirname(__file__)))
from  tcpserver import Tcpserver
if __name__ == '__main__':
    Tcpserver.start_server()