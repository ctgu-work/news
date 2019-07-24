# coding:utf8
from app import app
from flask import render_template


@app.route('/')
def index():
    return render_template("index.html")
    # return "Hellosdf"


if __name__ == "__main__":
    app.run()