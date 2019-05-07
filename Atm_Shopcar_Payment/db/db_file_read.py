from core import user_logging
from lib import log_user
import os,json
Path1=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
log1=r"atm_shopcar_payment\log\数据库读.log"
Logpath=os.path.join(Path1,log1)
def db_read(db_file_baihu,db_file_heihu):
    dic_baihu={}
    dic_heihu={}
    logger=log_user.getlog(Logpath,"db_read")
    logger.info("打开数据库读取白户信息")
    with open(db_file_baihu,encoding="utf-8") as line:
        dic_baihu.update(json.load(line))
    logger.info("打开数据库读取白户信息已完成")
    logger.info("打开数据库读取黑户信息")
    with open(db_file_heihu,encoding="utf-8") as line1:
        if os.path.getsize(db_file_heihu) != 0:
            dic_heihu.update(json.load(line1))
    logger.info("打开数据库读取黑户信息已完成")
    logger.info("进入登录函数")
    user_logging.loging(dic_baihu,dic_heihu)
if __name__ == '__main__':
    db_read()
