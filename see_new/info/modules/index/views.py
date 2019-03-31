from info import redis_store
from . import index_blu
from flask import render_template
from flask import current_app

@index_blu.route('/')
def index():
    # session["name"]="apple"
    # logging.debug("测试日志")
    # flask.current_app.logger.error("saasd")
    # redis_store.set("name","asdsd")
    return render_template('news/index.html')

@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file("news/favicon.ico")