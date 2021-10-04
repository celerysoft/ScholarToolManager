#!/usr/bin/python3
# -*-coding:utf-8 -*-
import logging

from flask import Flask, redirect, url_for, make_response, Blueprint
from werkzeug.utils import find_modules, import_string

import configs
from application.exception.api import BaseApiException
from application.util import shadowsocks_controller, database
from application.util.database import session_scope
from application.views.base_api import BaseView

BASE_URL = configs.BASE_URL


def derive_import_root(current_name):
    return '.'.join(current_name.split('.')[:-1])


def add_url_rules_for_blueprint(root, blueprint: Blueprint):
    for name in find_modules(root, recursive=True):
        mod = import_string(name)
        if hasattr(mod, 'view') and isinstance(mod.view, type(BaseView)):
            add_url_rule_for_blueprint(root, mod.view, name, blueprint)


def add_url_rule_for_blueprint(root: str, view, import_name: str, blueprint: Blueprint, log: bool = False):
    # if the view's import name is application.views.user.user
    # so that the Blueprint's url_prefix is /user
    # make sure the view's url is /user other than /user/user
    import_names = import_name.split('.')
    if len(import_names) >= 2 and import_names[-1] == import_names[-2]:
        import_names = import_names[:-1]
        import_name = '.'.join(import_names)

    index = import_name.find(root)
    if index != -1:
        url = import_name[len(root):]
    else:
        url = import_name
    while url.startswith('.'):
        url = url[1:]
    if len(url) > 0:
        urls = url.split('.')
        length = len(urls)
        url = '/{}' * length
        url = url.format(*urls)
    else:
        url = ''
    if log:
        print('url => "{}"'.format(url))
    blueprint.add_url_rule(url, view_func=view.as_view(view.__name__))


def add_url_rules_and_register_blueprints(root: str, flask_app: Flask):
    root_depth = len(root.split('.'))
    for name in find_modules(root, recursive=True):
        module_depth = len(name.split('.'))
        depth_difference = module_depth - root_depth
        if depth_difference in (1, 2):
            mod = import_string(name)
            if depth_difference == 1 and hasattr(mod, 'view') and isinstance(mod.view, type(BaseView)):
                add_url_rule(mod.view, name, root, flask_app)
            elif depth_difference == 2 and hasattr(mod, 'bp') and isinstance(mod.bp, Blueprint):
                register_blueprint(mod.bp, name, root, flask_app)


def add_url_rule(view, import_name: str, root: str, flask_app: Flask, log: bool = False):
    # when handling the view's(blueprint's) path to url, need to ignore application/views
    # we want the url of the view application/views/login.py is '/login' not '/application/views/login'
    index = import_name.find(root)
    if index != -1:
        url = import_name[len(root):]
    else:
        url = import_name
    while url.startswith('.'):
        url = url[1:]

    urls = url.split('.')
    length = len(urls)
    if length > 0:
        url = '/{}' * length
        url = url.format(*urls)
        url = '{}{}'.format(BASE_URL, url)
        if log:
            print(url)
        flask_app.add_url_rule(url, view_func=view.as_view(import_name))


def register_blueprint(blueprint: Blueprint, import_name: str, root: str, flask_app: Flask, log: bool = False):
    index = import_name.find(root)
    if index != -1:
        url = import_name[len(root):]
    else:
        url = import_name
    while url.startswith('.'):
        url = url[1:]
    urls = url.split('.')
    length = len(urls)

    # if the bp's import name is application.views.user.user
    # make sure the url_prefix is /user other than /user/user
    if length >= 2 and urls[-1] == urls[-2]:
        urls = urls[:-1]
        length = len(urls)

    if length > 0:
        prefix = '/{}' * length
        prefix = prefix.format(*urls)
        prefix = '{}{}'.format(BASE_URL, prefix)
        if log:
            print(prefix)
        flask_app.register_blueprint(blueprint, url_prefix=prefix)


# def register_cacheable_model(root):
#     def after_update_listener(mapper, connection, target):
#         # 数据库更新时将缓存删除
#         cache.delete_model(target)
#
#     for name in find_modules(root, recursive=True):
#         mod = import_string(name)
#         if hasattr(mod, 'cacheable'):
#             event.listen(mod.cacheable, 'after_update', after_update_listener)


def init_logging(flask_app: Flask):
    handler = logging.FileHandler(configs.LOG_FILE, encoding='UTF-8')
    handler.setLevel(logging.WARNING)
    logging_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    handler.setFormatter(logging_format)
    flask_app.logger.addHandler(handler)


def action_before_app_run(flask_app):
    with session_scope() as db_session:
        shadowsocks_controller.recreate_shadowsocks_config_file(db_session, flask_app.debug)


def create_app():
    """
    生成app实例

    :return:
    """
    flask_app = Flask(__name__)
    flask_app.config.from_object('configs')

    init_logging(flask_app)

    if configs.DEBUG:
        def after_request(resp):
            # Enable CORS supported
            resp.headers['Access-Control-Allow-Origin'] = '*'
            resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            resp.headers['Access-Control-Allow-Credentials'] = True
            resp.headers['Access-Control-Max-Age'] = 1728000
            resp.headers['Access-Control-Allow-Headers'] = (
                'DNT,X-Custom-Header,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,'
                'Content-Type,Authorization'
            )

            return resp
        flask_app.after_request(after_request)

    add_url_rules_and_register_blueprints('application.views', flask_app)

    action_before_app_run(flask_app)

    return flask_app


app = create_app()


# -------------------------------------------------- Error Handler -------------------------------------------------- #
# -------------------------------------------------- Error Handler -------------------------------------------------- #
# -------------------------------------------------- Error Handler -------------------------------------------------- #
# -------------------------------------------------- Error Handler -------------------------------------------------- #
# -------------------------------------------------- Error Handler -------------------------------------------------- #
@app.errorhandler(Exception)
def handle_base_exception(error):
    app.logger.exception(error)


# ------------------------------------------------ API Error Handler ------------------------------------------------ #
@app.errorhandler(BaseApiException)
def handle_api_exception(error):
    if configs.BUILD_API_EXCEPTION:
        app.logger.exception(error)
    return make_response(error.to_response())

if __name__ == '__main__':
    error_message = """
    Don't run app.py directly. 
    Use "FLASK_APP=manage.py;FLASK_DEBUG=1 python -m flask run --host 127.0.0.1 --port 12345" to serve the app.
    """
    raise RuntimeError(error_message)
