from flask import Flask, redirect, url_for

app = Flask(__name__)


@app.route('/')
def home_page():
    return 'Hello World!'


@app.route('/index/')
def index():
    return redirect(url_for('home_page'))


if __name__ == '__main__':
    app.run()
