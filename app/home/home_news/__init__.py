from flask import Blueprint

home_news = Blueprint("/news",__name__)

import app.home.home_news.views