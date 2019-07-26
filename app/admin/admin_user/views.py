from . import admin_user


@admin_user.route('/test1')
def test1():
    return "admin_user"