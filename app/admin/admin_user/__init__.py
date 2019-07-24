from flask import Blueprint

admin_user = Blueprint("admin/user",__name__)

import app.admin.admin_user.views