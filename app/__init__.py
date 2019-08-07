# coding:utf8
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from config import config
import logging

from app.home.home_user import home_user
from app.home.home_news import home_news
from app.home.home_index import home_index
from app.admin.admin_user import admin_user
from app.admin.admin_news import admin_news

from app.home.home_index import *
from app.home.home_news import *
from app.home.home_user import *


def create_app(config_name):
    app = Flask(__name__)
    # 加载配置文件
    app.config.from_object(config["development"])

    # 注册蓝图
    app.register_blueprint(home_news, url_prefix="/news")
    app.register_blueprint(home_index, url_prefix="/index")
    app.register_blueprint(home_user, url_prefix="/user")

    admin = NestableBlueprint('admin', __name__, url_prefix='/admin')
    admin.register_blueprint(admin_user, url_prefix="/user")
    admin.register_blueprint(admin_news, url_prefix="/news")
    app.register_blueprint(admin)
    return app


app = create_app("development")
db = SQLAlchemy(app)

# 日志系统配置
handler = logging.FileHandler('app.log', encoding='UTF-8')
logging_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
handler.setFormatter(logging_format)
app.logger.addHandler(handler)


# 配置404界面
@app.errorhandler(404)
def page_not_found(e):
    return render_template("/news/404.html"), 404


# 配置500界面
@app.errorhandler(500)
def server_error(e):
    return render_template("/news/500.html"), 500
