from . import home_index
from flask import render_template


@home_index.route('/')
def test1():
    return render_template("home/index.html")