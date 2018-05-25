import click
import os

from app import create_app

# 通过配置创建 app
from util import static_file_hash_util

DEBUG = os.environ.get('FLASK_DEBUG', 1)
app = None
if DEBUG == 0:
    app = create_app('configs.ProductionConfig')
else:
    app = create_app('configs.DevelopmentConfig')


@app.cli.command()
def hello():
    print('Hello, commander!')


@app.cli.command()
def status():
    global app
    print('DEBUG = %s, TESTING = %s'
          % (app.config['DEBUG'], app.config['TESTING']))


@app.cli.command()
# @click.option('--count', default=1, help='Number of greetings.')
@click.option('--type', type=click.INT, prompt='Type(0-cdn, 1-local)', help='Where do the static files locate')
def generate_static_file(**kwargs):
    generate_type = kwargs.get('type', 0)
    if generate_type not in [0, 1]:
        return print('Unknown generate type!!!')

    command = static_file_hash_util.Command()
    command.execute(generate_type)
