from flask import Blueprint

home_index = Blueprint("/index",__name__)

import app.home.home_index.views