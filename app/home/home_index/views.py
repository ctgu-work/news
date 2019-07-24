from . import home_index

@home_index.route('/test1')
def test1():
    return "test1"