from . import home_user

@home_user.route('/test1')
def test1():
    return "user"