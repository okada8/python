import os
import sys
# 添加根目录到环境变量
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from views import src



if __name__ == '__main__':
    src.run()
