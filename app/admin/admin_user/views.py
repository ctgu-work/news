from . import admin_user
from flask import render_template
@admin_user.route('/test1')
def test1():
    return "admin_user"



