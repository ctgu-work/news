from . import admin_news


@admin_news.route('/test1')
def test1():
    return "admin_news"