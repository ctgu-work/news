from flask import Blueprint

admin_news = Blueprint("admin/news",__name__)

import app.admin.admin_news.views