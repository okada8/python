import sys,os
BASE_DIR=os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)
from conf import settings
from db import db_file_read
from lib import log_user
Path1=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
log1=r"atm_shopcar_payment\log\启动.log"
Logpath=os.path.join(Path1,log1)
def start1():
    db_file_read.db_read(settings.db_file_baihu2, settings.db_file_heihu2)
if __name__ == '__main__':
    logger=log_user.getlog(Logpath,"start")
    logger.info("开始运行程序")
    start1()
else:
    logger = log_user.getlog(Logpath, "start2")
    logger.info("解锁后开始运行程序")
    start1()


