import logging
def getlog(file,name):
    logger=logging.getLogger(name)
    logger.setLevel(10)
    fmt1 = logging.Formatter('[%(asctime)s][%(threadName)s:%(thread)d][task_id:%(name)s][%(filename)s:%(lineno)d]' \
                            '[%(levelname)s][%(message)s]')
    handler1=logging.FileHandler(file,encoding="utf-8")
    handler1.setFormatter(fmt1)
    logger.addHandler(handler1)

    return logger

























