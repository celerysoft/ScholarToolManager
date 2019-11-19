# -*-coding:utf-8 -*-
"""
FLASK_APP=manage.py flask hello
FLASK_APP=manage.py flask status
"""
import click

from app import app as flask_app

from application.util import static_file_hash_util

app = flask_app


@app.cli.command()
def hello():
    print('Hello, commander!')


@app.cli.command()
def status():
    global app
    print('DEBUG = %s, TESTING = %s'
          % (app.config['DEBUG'], app.config['TEST']))


@app.cli.command()
# @click.option('--count', default=1, help='Number of greetings.')
@click.option('--type', type=click.INT, prompt='Type(0-cdn, 1-local)', help='Where do the static files locate')
def generate_static_file(**kwargs):
    generate_type = kwargs.get('type', 0)
    if generate_type not in [0, 1]:
        return print('Unknown generate type!!!')

    command = static_file_hash_util.Command()
    command.execute(generate_type)
