# -*-coding:utf-8 -*-
"""
FLASK_APP=manage.py flask hello
FLASK_APP=manage.py flask status

静态资源版本更新
每次.js，.css，或者其他静态资源有变动时，需要执行这条命令进行静态资源版本更新
FLASK_APP=manage.py flask generate_static_file --type 0
"""
import click

from app import app as flask_app

from application.util import static_file_hash_util, init_project

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


@app.cli.command()
def create():
    success = init_project.toolkit.create_config_file()
    if success:
        print('Config file creation accomplish, please open the config file and configure the project, '
              'after you finish the config file, use "FLASK_APP=manage.py flask init" command to continue.')


@app.cli.command()
def init():
    success = init_project.toolkit.execute()
    if success:
        print('Project initialization succeed, you can now login with\n'
              'username: admin\n'
              'password: 12345679\n')
