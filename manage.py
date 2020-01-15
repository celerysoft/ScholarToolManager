# -*-coding:utf-8 -*-
"""
# 创建本地配置文件
FLASK_APP=manage.py flask create
# 补充完本地配置文件后，执行项目初始化
FLASK_APP=manage.py flask init

FLASK_APP=manage.py flask hello
FLASK_APP=manage.py flask status

静态资源版本更新
每次.js，.css，或者其他静态资源有变动时，需要执行这条命令进行静态资源版本更新
FLASK_APP=manage.py flask generate_static_file --type 0
"""
import click

from app import app as flask_app
from application.model.user import User

from application.util import static_file_hash_util, init_project, transfer_legacy_data, authorization
from application.util.database import session_scope

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


@app.cli.command()
@click.option('--username', type=click.STRING, prompt='username', help='username')
@click.option('--expires', type=click.INT, prompt='token expires in hours', help='token expires in hours')
def derive_user_jwt(**kwargs):
    username = kwargs.get('username', None)
    expires = kwargs.get('expires', 0)

    with session_scope() as session:
        user = session.query(User).filter(
            User.username == username,
            User.status != User.STATUS.DELETED
        ).first()  # type: User

        if user is None:
            print('Error: the user(username: {}) is not found.'.format(username))
            exit(1)

        token = authorization.toolkit.derive_jwt_token(
            uuid=user.uuid,
            expired_in=expires,
        )
        print(token)

@app.cli.command()
def transfer_former_database():
    success = transfer_legacy_data.toolkit.execute()
    if success:
        print('Data transferring accomplish.')
    else:
        print('Error: data transferring failed.')
