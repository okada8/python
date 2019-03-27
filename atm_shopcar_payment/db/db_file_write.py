from conf import settings
from lib import log_user
import os,json
Path1=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
log1=r"atm_shopcar_payment\log\数据库写.log"
Logpath=os.path.join(Path1,log1)
def db_write(dic_baihu,*args):
    logger=log_user.getlog(Logpath,"dbwrite")
    with open(settings.db_file_baihu2, "w") as line:
            if not args:
                json.dump(dic_baihu, line)
                logger.info("数据库写入成功")
                return True
            else:
                with open(settings.db_file_baihu2, "a") as f2:
                    json.dump(dic_baihu,f2)
                dic_heihu = args[0]
                with open(settings.db_file_heihu2, "w") as line1:
                    json.dump(dic_heihu,line1)
                logger.info("数据库写入成功")
                return True