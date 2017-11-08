#!/usr/bin/python3
# -*-coding:utf-8 -*-

from flask_script import Manager, Shell

from app import create_app

# 通过配置创建 app
# app = create_app('configs.DevelopmentConfig')
app = create_app('configs.ProductionConfig')
manager = Manager(app)


def make_shell_context():
    return dict(app=app)


manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def hello():
    print('Hello, commander!')


@manager.command
def status():
    global app
    print('DEBUG = %s, TESTING = %s'
          % (app.config['DEBUG'], app.config['TESTING']))


@manager.command
def deploy():
    """Run deployment tasks."""
    pass


if __name__ == '__main__':
    manager.run()
