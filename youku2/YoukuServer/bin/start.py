import os,sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core import server


if __name__ == "__main__":
    server.run_server()




