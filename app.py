#!/usr/bin/python3
# -*-coding:utf-8 -*-
import logging

from flask import Flask, redirect, url_for, session, g, current_app
from flask.json import jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import exception.http
import init_app
import permission
from util import shadowsocks_controller
from view import views, method_views

app = Flask(__name__)
app.config.from_object('configs.Config')

# __SESSION_KEY = app.config['SECRET_KEY']
# __SHA1_PASSWORD_SALT = app.config['SHA1_SALT']
# __RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
# __RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')
# __ITEM_PER_PAGE = app.config['ITEM_PER_PAGE']

Session(app)

# db = SQLAlchemy(app)
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])


# def update_engine():
#     global engine
#     engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
#
#
# def derive_db_session(pagination=False):
#     if pagination:
#         return db.session
#     else:
#         return sessionmaker(bind=engine)()
# def derive_db_session(pagination=False):
#     if pagination:
#         db_session_with_pagination = getattr(g, '_db_session_with_pagination', None)
#         if db_session_with_pagination is None:
#             db_session_with_pagination = g._db_session_with_pagination = db.session
#         return db_session_with_pagination
#     else:
#         db_session = getattr(g, '_db_session', None)
#         if db_session is None:
#             db_session = g._db_session = scoped_session(sessionmaker(bind=engine))
#         return db_session
#
#
# def derive_user_id_from_session(call_by_api=False):
#     if call_by_api:
#         permission.check_user_api_permission()
#     else:
#         permission.check_user_permission()
#     return session['user']['id']
#
#
# def derive_app_logger():
#     app_logger = getattr(g, '_app_logger', None)
#     if app_logger is None:
#         app_logger = g._app_logger = app.logger
#     return app_logger


def action_before_app_run():
    shadowsocks_controller.recreate_shadowsocks_config_file(sessionmaker(bind=engine)(), app.debug)


def create_app(config='configs.DevelopmentConfig'):
    """
    生成app实例
    :param config: 'configs.DevelopmentConfig' or 'configs.ProductionConfig'
    :return:
    """
    # app.config.from_object('configs.DevelopmentConfig')
    # app.config.from_object('configs.ProductionConfig')
    app.config.from_object(config)

    handler = logging.FileHandler(app.config['LOG_FILE'], encoding='UTF-8')
    handler.setLevel(logging.WARNING)
    logging_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    handler.setFormatter(logging_format)
    app.logger.addHandler(handler)

    global engine
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

    init_app.init_jinja2()
    init_app.init_jinja2_global(app)
    init_app.init_views(app)
    init_app.init_method_views(app)

    action_before_app_run()
    return app


@app.teardown_appcontext
def teardown_db(exception=None):
    db_session = getattr(g, '_db_session', None)
    if db_session is not None:
        db_session.remove()

    db_session_with_pagination = getattr(g, '_db_session_with_pagination', None)
    if db_session_with_pagination is not None:
        db_session_with_pagination.remove()

    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# -------------------------------------------------- Error Handler -------------------------------------------------- #
# -------------------------------------------------- Error Handler -------------------------------------------------- #
# -------------------------------------------------- Error Handler -------------------------------------------------- #
# -------------------------------------------------- Error Handler -------------------------------------------------- #
# -------------------------------------------------- Error Handler -------------------------------------------------- #


@app.errorhandler(Exception)
def handle_base_exception(error):
    app.logger.exception(error)


# ------------------------------------------------ Page Error Handler ------------------------------------------------ #


@app.errorhandler(exception.http.Unauthorized)
def handle_unauthorized(error):
    return redirect(url_for('login'))


@app.errorhandler(exception.http.Forbidden)
def handle_unauthorized(error):
    return redirect(url_for('login'))


# ------------------------------------------------ Api Error Handler ------------------------------------------------ #


@app.errorhandler(exception.api.Unauthorized)
def handle_api_unauthorized(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(exception.api.Forbidden)
def handle_api_unauthorized(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(exception.api.InvalidRequest)
def handle_api_unauthorized(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


# -------------------------------------------------- PAGE -------------------------------------------------- #
# -------------------------------------------------- PAGE -------------------------------------------------- #
# -------------------------------------------------- PAGE -------------------------------------------------- #
# -------------------------------------------------- PAGE -------------------------------------------------- #
# -------------------------------------------------- PAGE -------------------------------------------------- #


@app.route('/logout/')
def logout():
    session.pop('user', None)
    return redirect(url_for('home_page'))


# @app.route('/')
# def home_page1():
#     permission.check_user_permission()
#
#     return render_template('index.html',
#                            title='主页')


app.add_url_rule('/', view_func=views.UserView.as_view('home_page', 'index.html', '主页'))

app.add_url_rule('/login/', view_func=views.LoginView.as_view('login'))
app.add_url_rule('/register/', view_func=views.RegisterView.as_view('register'))
app.add_url_rule('/manage/', view_func=views.PermissionRequiredView.as_view('manage', 'manage.html', '后台管理',
                                                                            permission.check_manage_permission))
app.add_url_rule('/manage/invitation/', view_func=views.ManageInvitationView.as_view('manage_invitation'))
app.add_url_rule('/manage/role/', view_func=views.ManageRoleView.as_view('manage_role'))
app.add_url_rule('/manage/role/create/',
                 view_func=views.PermissionRequiredView.as_view('create_role',
                                                                'manage_role_edit.html',
                                                                '创建角色',
                                                                permission.check_manage_role_permission,
                                                                action='POST'))
app.add_url_rule('/manage/role/edit/', view_func=views.EditRoleView.as_view('edit_role'))
app.add_url_rule('/manage/service-template/', view_func=views.ManageServiceTemplateView.as_view('manage_service_template'))
app.add_url_rule('/manage/service-template/create/',
                 view_func=views.CreateServiceTemplateView.as_view('create_service_template'))
app.add_url_rule('/manage/service-template/edit/',
                 view_func=views.EditServiceTemplateView.as_view('edit_service_template'))
app.add_url_rule('/manage/event/',
                 view_func=views.ManageEventView.as_view('manage_event'))
app.add_url_rule('/manage/event/create/',
                 view_func=views.PermissionRequiredView.as_view('create_event',
                                                                'manage_event_edit.html',
                                                                '发布公告',
                                                                permission.check_manage_event_permission,
                                                                action='POST'))
app.add_url_rule('/manage/event/edit/',
                 view_func=views.EditEventView.as_view('edit_event'))


app.add_url_rule('/manage/user/',
                 view_func=views.ManageUserView.as_view('manage_user'))
app.add_url_rule('/user/<name>',
                 view_func=views.UserProfileView.as_view('user_profile'))
app.add_url_rule('/event/',
                 view_func=views.EventView.as_view('event'))
app.add_url_rule('/event/<int:event_id>',
                 view_func=views.EventDetailView.as_view('event_detail'))
app.add_url_rule('/product/', view_func=views.UserView.as_view('product', 'product.html', '我的学术'))
app.add_url_rule('/product/detail/<service_id>',
                 view_func=views.ProductDetailView.as_view('product_detail'))
app.add_url_rule('/product/create/',
                 view_func=views.CreateProductView.as_view('create_product'))
app.add_url_rule('/product/create/pay/<service_template_id>',
                 view_func=views.PayProductView.as_view('pay_product'))
app.add_url_rule('/product/renew/pay/<service_id>',
                 view_func=views.RenewProductView.as_view('renew_product'))
app.add_url_rule('/agreement/', view_func=views.BaseView.as_view('agreement', 'agreement.html', '用户协议'))
app.add_url_rule('/manage/usage/', view_func=views.PermissionRequiredView.as_view('manage_usage',
                                                                                  'manage_usage.html', '流量管理',
                                                                                  permission.check_manage_permission))

# -------------------------------------------------- API -------------------------------------------------- #
# -------------------------------------------------- API -------------------------------------------------- #
# -------------------------------------------------- API -------------------------------------------------- #
# -------------------------------------------------- API -------------------------------------------------- #
# -------------------------------------------------- API -------------------------------------------------- #


app.add_url_rule('/api/grecaptcha', view_func=method_views.ReCaptchaApi.as_view('api_g_re_captcha'))
app.add_url_rule('/api/today-in-history', view_func=method_views.TodayInHistoryAPI.as_view('api_today_in_history'))
app.add_url_rule('/api/login', view_func=method_views.LoginAPI.as_view('api_login'))
app.add_url_rule('/api/register', view_func=method_views.RegisterAPI.as_view('api_register'))
app.add_url_rule('/api/user', view_func=method_views.UserAPI.as_view('api_user'))
app.add_url_rule('/api/invitation', view_func=method_views.InvitationCodeAPI.as_view('api_invitation'))
app.add_url_rule('/api/permission', view_func=method_views.PermissionAPI.as_view('api_permission'))
app.add_url_rule('/api/event', view_func=method_views.EventAPI.as_view('api_event'))
app.add_url_rule('/api/role', view_func=method_views.RoleAPI.as_view('api_role'))
app.add_url_rule('/api/service-template', view_func=method_views.ServiceTemplateAPI.as_view('api_service_template'))
app.add_url_rule('/api/service', view_func=method_views.ServiceAPI.as_view('api_service'))
app.add_url_rule('/api/usage', view_func=method_views.UsageAPI.as_view('api_usage'))
app.add_url_rule('/api/scholar-balance', view_func=method_views.ScholarBalanceAPI.as_view('api_scholar_balance'))
app.add_url_rule('/api/service-password', view_func=method_views.ServicePasswordAPI.as_view('api_service_password'))


if __name__ == '__main__':
    create_app()
    # create_app('configs.ProductionConfig')
    host = app.config['HOST']
    port = app.config['PORT']
    processes = app.config['PROCESSES']

    app.run(host=host, port=port, processes=processes)
