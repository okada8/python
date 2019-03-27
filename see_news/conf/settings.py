import os
BASE_PATH=os.path.dirname(os.path.dirname(__file__))
USER_PATH=os.path.join(BASE_PATH,"db","user_date.json")
NEW_PATH=os.path.join(BASE_PATH,"db","news_date.json")
MY_INI=os.path.join(BASE_PATH,"db","my.ini")
ADMIN_LOG=os.path.join(BASE_PATH,"log","Admin.log")
USER_LOG=os.path.join(BASE_PATH,"log","User.log")
