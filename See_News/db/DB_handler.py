from conf import settings
import json
import configparser

def admin_log_read():
    with open(settings.ADMIN_LOG,"r", encoding="utf-8") as line:
        f = line.read()
        return f

def user_log_read():
    with open(settings.USER_LOG,"r", encoding="utf-8") as line:
        f = line.read()
        return f

def get_user_read():
    with open(settings.USER_PATH,"r",encoding="utf-8") as line:
        dic_user=json.load(line)
    return dic_user

def get_user_write(dic_user):
    with open(settings.USER_PATH,"w",encoding="utf-8") as line:
         json.dump(dic_user,line)
    return True

def get_news_read():
    with open(settings.NEW_PATH, "r", encoding="utf-8") as line:
        dic_news=json.load(line)
    return dic_news

def get_news_write(dic_news):
    with open(settings.NEW_PATH,"w",encoding="utf-8") as line:
        json.dump(dic_news,line)
    return True

def myini_read():
    cfg = configparser.ConfigParser()
    cfg.read(settings.MY_INI, encoding="utf-8")
    return cfg

def myini_write(cfg):
    with open(settings.MY_INI, "wt", encoding="utf-8") as f:
        cfg.write(f)
    return True

def collection_read(username):
    cfg=myini_read()
    if cfg.has_section(username) == True:
        shoucang = cfg.get(username, "shoucang")
        s=shoucang.split("|")
        return cfg,s
    else:
        return cfg

def collection_write(username,new_name):
    cfg,res=collection_read(username)
    if new_name in res:
        print("已经收藏过了")
    else:
        res.append(new_name)
        g="|".join(res)
        cfg.set(username,"shoucang",g)
        myini_write(cfg)
        return True

def user_zhuce_ini(username):
    cfg=collection_read(username)
    cfg.add_section(username)
    cfg.set(username, "shoucang","")
    myini_write(cfg)
    return True

if __name__ == '__main__':
    collection_read("apple")