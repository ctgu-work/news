from . import home_news

@home_news.route('/test1')
def test1():
    return "test1"