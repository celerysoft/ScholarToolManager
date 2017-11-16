#!/usr/bin/python3
# -*-coding:utf-8 -*-
import logging

import markdown2
from flask import Flask, redirect, url_for, render_template, session, request, abort, g
from flask.json import jsonify
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

import exception.api
import exception.http
import init_app
import model
import permission
from util import shadowsocks_controller
from view import views, method_views

app = Flask(__name__)
app.config.from_object('configs.Config')

# __SESSION_KEY = app.config['SECRET_KEY']
# __SHA1_PASSWORD_SALT = app.config['SHA1_SALT']
# __RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
# __RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')
__ITEM_PER_PAGE = app.config['ITEM_PER_PAGE']

Session(app)

db = SQLAlchemy(app)
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])


def update_engine():
    global engine
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])


# def derive_db_session(pagination=False):
#     if pagination:
#         return db.session
#     else:
#         return sessionmaker(bind=engine)()
def derive_db_session(pagination=False):
    if pagination:
        db_session_with_pagination = getattr(g, '_db_session_with_pagination', None)
        if db_session_with_pagination is None:
            db_session_with_pagination = g._db_session_with_pagination = db.session
        return db_session_with_pagination
    else:
        db_session = getattr(g, '_db_session', None)
        if db_session is None:
            db_session = g._db_session = scoped_session(sessionmaker(bind=engine))
        return db_session


def derive_user_id_from_session(call_by_api=False):
    if call_by_api:
        permission.check_user_api_permission()
    else:
        permission.check_user_permission()
    return session['user']['id']


def derive_app_logger():
    app_logger = getattr(g, '_app_logger', None)
    if app_logger is None:
        app_logger = g._app_logger = app.logger
    return app_logger


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


@app.route('/')
def home_page1():
    permission.check_user_permission()

    return render_template('index.html',
                           title='主页')


app.add_url_rule('/', view_func=views.BaseView.as_view('home_page', 'index.html', '主页'))
app.add_url_rule('/login/', view_func=views.BaseView.as_view('login', 'login.html', '登录'))
app.add_url_rule('/register/', view_func=views.BaseView.as_view('register', 'register.html', '注册'))


app.add_url_rule('/manage/', view_func=views.PermissionRequiredView.as_view('manage', 'manage.html', '后台管理',
                                                                            permission.check_manage_permission))
# @app.route('/manage/')
# def manage():
#     if not permission.check_manage_permission(derive_db_session(), derive_user_id_from_session()):
#         return redirect(url_for('home_page'))
#
#     return render_template('manage.html',
#                            title='后台管理')


app.add_url_rule('/manage/invitation/', view_func=views.ManageInvitationView.as_view('manage_invitation'))
# @app.route('/manage/invitation/')
# def manage_invitation():
#     db_session = derive_db_session(pagination=True)
#     if not permission.check_manage_invitation_code_permission(db_session, derive_user_id_from_session()):
#         raise exception.http.Forbidden()
#
#     page = request.args.get('page')
#     try:
#         page = int(page) if page is not None else 1
#     except ValueError:
#         return redirect(url_for('manage_invitation'))
#
#     pagination = db_session.query(model.InvitationCode).order_by(model.InvitationCode.created_at.desc()).paginate(
#         page, __ITEM_PER_PAGE, False)
#     if page > 1 and len(pagination.items) is 0:
#         return redirect(url_for('manage_invitation'))
#     else:
#         for invitation in pagination.items:
#             inviter = db_session.query(model.User).filter_by(id=invitation.inviter_id).first()
#             invitation.inviter_username = inviter.username
#             if invitation.invitee_id is not None:
#                 invitee = db_session.query(model.User).filter_by(id=invitation.invitee_id).first()
#                 invitation.invitee_username = invitee.username
#
#     return render_template('manage_invitation.html',
#                            title='邀请码管理',
#                            pagination=pagination,
#                            pagination_url_for='manage_invitation')


app.add_url_rule('/manage/role/', view_func=views.ManageRoleView.as_view('manage_role'))
# @app.route('/manage/role/')
# def manage_role():
#     db_session = derive_db_session(pagination=True)
#     if not permission.check_manage_role_permission(db_session, derive_user_id_from_session()):
#         raise exception.http.Forbidden()
#
#     page = request.args.get('page')
#     try:
#         page = int(page) if page is not None else 1
#     except ValueError:
#         return redirect(url_for('manage_role'))
#
#     pagination = db_session.query(model.Role).order_by(model.Role.id).paginate(
#         page, __ITEM_PER_PAGE, False)
#     if page > 1 and len(pagination.items) is 0:
#         return redirect(url_for('manage_role'))
#
#     return render_template('manage_role.html',
#                            title='角色管理',
#                            pagination=pagination,
#                            pagination_url_for='manage_role')


app.add_url_rule('/manage/role/create/',
                 view_func=views.PermissionRequiredView.as_view('create_role',
                                                                'manage_role_edit.html',
                                                                '创建角色',
                                                                permission.check_manage_role_permission,
                                                                action='POST'))
# @app.route('/manage/role/create/')
# def create_role():
#     if not permission.check_manage_role_permission(derive_db_session(), derive_user_id_from_session()):
#         return redirect(url_for('home_page'))
#
#     return render_template('manage_role_edit.html',
#                            title='创建角色',
#                            action='POST')


app.add_url_rule('/manage/role/edit/', view_func=views.EditRoleView.as_view('edit_role'))
# @app.route('/manage/role/edit/')
# def edit_role():
#     if not permission.check_manage_role_permission(derive_db_session(), derive_user_id_from_session()):
#         return redirect(url_for('home_page'))
#
#     role_id = request.args.get('id')
#     return render_template('manage_role_edit.html',
#                            title='编辑角色',
#                            id=role_id,
#                            action='PATCH')


app.add_url_rule('/manage/service-template/', view_func=views.ManageServiceTemplateView.as_view('manage_service_template'))
# @app.route('/manage/service-template/')
# def manage_service_template():
#     db_session = derive_db_session(pagination=True)
#     if not permission.check_manage_service_template_permission(db_session, derive_user_id_from_session()):
#         raise exception.http.Forbidden()
#
#     page = request.args.get('page')
#     try:
#         page = int(page) if page is not None else 1
#     except ValueError:
#         return redirect(url_for('manage_service_template'))
#
#     pagination = db_session.query(model.ServiceTemplate).order_by(model.ServiceTemplate.id).paginate(
#         page, __ITEM_PER_PAGE, False)
#     if page > 1 and len(pagination.items) is 0:
#         return redirect(url_for('manage_service_template'))
#
#     return render_template('manage_service_template.html',
#                            title='套餐模版管理',
#                            pagination=pagination,
#                            pagination_url_for='manage_service_template')


app.add_url_rule('/manage/service-template/create/',
                 view_func=views.CreateServiceTemplateView.as_view('create_service_template'))
# @app.route('/manage/service-template/create/')
# def create_service_template():
#     if not permission.check_manage_service_template_permission(derive_db_session(), derive_user_id_from_session()):
#         raise exception.http.Forbidden()
#
#     service_type = request.args.get('type') if request.args.get('type') else 0
#
#     return render_template('manage_service_template_edit.html',
#                            title='创建套餐',
#                            type=service_type,
#                            action='POST')


app.add_url_rule('/manage/service-template/edit/',
                 view_func=views.EditServiceTemplateView.as_view('edit_service_template'))
# @app.route('/manage/service-template/edit/')
# def edit_service_template():
#     if not permission.check_manage_service_template_permission(derive_db_session(), derive_user_id_from_session()):
#         raise exception.http.Forbidden()
#
#     service_template_id = request.args.get('id')
#
#     return render_template('manage_service_template_edit.html',
#                            title='编辑套餐',
#                            id=service_template_id,
#                            action='PATCH')


app.add_url_rule('/manage/event/',
                 view_func=views.ManageEventView.as_view('manage_event'))
# @app.route('/manage/event/')
# def manage_event():
#     db_session = derive_db_session(pagination=True)
#     if not permission.check_manage_event_permission(db_session, derive_user_id_from_session()):
#         raise exception.http.Forbidden()
#
#     page = request.args.get('page')
#     try:
#         page = int(page) if page is not None else 1
#     except ValueError:
#         return redirect(url_for('manage_event'))
#
#     pagination = db_session.query(model.Event).order_by(model.Event.created_at.desc()).paginate(
#         page, __ITEM_PER_PAGE, False)
#     if page > 1 and len(pagination.items) is 0:
#         return redirect(url_for('manage_event'))
#     else:
#         for product in pagination.items:
#             user = db_session.query(model.User).filter_by(id=product.user_id).first()
#             product.user_name = user.name
#
#     return render_template('manage_event.html',
#                            title='公告管理',
#                            pagination=pagination,
#                            pagination_url_for='manage_event')


app.add_url_rule('/manage/event/create/',
                 view_func=views.PermissionRequiredView.as_view('create_event',
                                                                'manage_event_edit.html',
                                                                '发布公告',
                                                                permission.check_manage_event_permission,
                                                                action='POST'))
# @app.route('/manage/event/create/')
# def create_event():
#     if not permission.check_manage_event_permission(derive_db_session(), derive_user_id_from_session()):
#         return redirect(url_for('home_page'))
#
#     return render_template('manage_event_edit.html',
#                            title='发布公告',
#                            action='POST')


app.add_url_rule('/manage/event/edit/',
                 view_func=views.EditEventView.as_view('edit_event'))
# @app.route('/manage/event/edit/')
# def edit_event():
#     if not permission.check_manage_event_permission(derive_db_session(), derive_user_id_from_session()):
#         return redirect(url_for('home_page'))
#
#     product_id = request.args.get('id')
#     return render_template('manage_event_edit.html',
#                            title='编辑公告',
#                            id=product_id,
#                            action='PATCH')


app.add_url_rule('/manage/user/',
                 view_func=views.ManageUserView.as_view('manage_user'))
# @app.route('/manage/user/')
# def manage_user():
#     db_session = derive_db_session(pagination=True)
#     if not permission.check_manage_user_permission(db_session, derive_user_id_from_session()):
#         return redirect(url_for('home_page'))
#
#     url = url_for('manage_user')
#     page = request.args.get('page')
#     try:
#         page = int(page) if page is not None else 1
#     except ValueError:
#         return redirect(url)
#
#     pagination = db_session.query(model.User).order_by(model.User.created_at).paginate(
#         page, __ITEM_PER_PAGE, False)
#     if page > 1 and len(pagination.items) is 0:
#         return redirect(url)
#
#     return render_template('manage_user.html',
#                            title='用户管理',
#                            pagination=pagination,
#                            pagination_url_for='manage_user')


app.add_url_rule('/user/<name>',
                 view_func=views.UserProfileView.as_view('user_profile'))
# @app.route('/user/<name>')
# def show_user_profile(name):
#     permission.check_user_permission()
#
#     db_session = derive_db_session()
#     user = db_session.query(model.User).filter_by(name=name).first()
#     if user is None:
#         return abort(404)
#
#     return render_template('user.html',
#                            title='用户' + name,
#                            user=user)


app.add_url_rule('/event/',
                 view_func=views.EventView.as_view('event'))
# @app.route('/event/')
# def event():
#     permission.check_user_permission()
#
#     page = request.args.get('page')
#     try:
#         page = int(page) if page is not None else 1
#     except ValueError:
#         return redirect(url_for('event'))
#
#     db_session = derive_db_session(pagination=True)
#     pagination = db_session.query(model.Event).order_by(model.Event.created_at.desc()).paginate(
#         page, __ITEM_PER_PAGE, False
#     )
#     if page > 1 and len(pagination.items) is 0:
#         return redirect(url_for('event'))
#
#     for evenet in pagination.items:
#         user = db_session.query(model.User).filter_by(id=evenet.user_id).first()
#         evenet.user_name = user.name
#         evenet.user_image = user.image
#
#     return render_template('event.html',
#                            title='公告',
#                            pagination=pagination,
#                            pagination_url_for='event')


app.add_url_rule('/event/<int:event_id>',
                 view_func=views.EventDetailView.as_view('event_detail'))
# @app.route('/event/<int:event_id>')
# def event_detail(event_id):
#     permission.check_user_permission()
#
#     db_session = derive_db_session()
#     event = db_session.query(model.Event).filter_by(id=event_id).first()
#     if event is None:
#         return abort(404)
#
#     user = db_session.query(model.User).filter_by(id=event.user_id).first()
#
#     event.html_content = markdown2.markdown(event.content, extras=['fenced-code-blocks', 'tables', 'toc'])
#
#     event.html_content = event.html_content.replace('{{ image }}', app.config['URL_OF_BLOG_IMAGE'])
#
#     event.tags = event.tag.split(' ')
#     event.user_name = user.name
#     event.user_image = user.image
#
#     return render_template('event_view.html',
#                            title='公告',
#                            event=event)


app.add_url_rule('/product/', view_func=views.UserView.as_view('product', 'product.html', '我的学术'))


app.add_url_rule('/product/detail/<service_id>',
                 view_func=views.ProductDetailView.as_view('product_detail'))
# @app.route('/product/detail/<service_id>')
# def product_detail(service_id):
#     # 防止查看不属于当前登录用户的套餐详情
#     user_id = derive_user_id_from_session()
#     db_session = derive_db_session()
#
#     user_service = db_session.query(model.UserService) \
#         .filter(model.Service.id == service_id) \
#         .filter(model.UserService.service_id == model.Service.id) \
#         .filter(model.UserService.user_id == user_id).first()
#     if user_service is None:
#         return redirect(url_for('product'))
#
#     return render_template('product_detail.html',
#                            service_id=service_id,
#                            title='学术详情')

app.add_url_rule('/product/create/',
                 view_func=views.CreateProductView.as_view('create_product'))
# @app.route('/product/create/')
# def create_product():
#     permission.check_user_permission()
#
#     db_session = derive_db_session()
#
#     monthly_services = db_session.query(model.ServiceTemplate) \
#         .filter(model.ServiceTemplate.type == model.ServiceTemplate.MONTHLY) \
#         .all()
#     for s in monthly_services:
#         s.descriptions = s.description.split('#')
#
#     data_services = db_session.query(model.ServiceTemplate) \
#         .filter(model.ServiceTemplate.type == model.ServiceTemplate.DATA) \
#         .all()
#     for s in data_services:
#         s.descriptions = s.description.split('#')
#
#     return render_template('product_create.html',
#                            monthly_services=monthly_services,
#                            data_services=data_services,
#                            title='获取新学术')


app.add_url_rule('/product/create/pay/<service_template_id>',
                 view_func=views.PayProductView.as_view('pay_product'))
# @app.route('/product/create/pay/<service_template_id>')
# def pay_product(service_template_id):
#     user_id = derive_user_id_from_session()
#
#     db_session = derive_db_session()
#     service_template = db_session.query(model.ServiceTemplate) \
#         .filter(model.ServiceTemplate.id == service_template_id).first()
#     if service_template is None:
#         return abort(404)
#     service_template.descriptions = service_template.description.split('#')
#     service_template.total_price = service_template.price + service_template.initialization_fee
#
#     user_scholar_balance = db_session.query(model.UserScholarBalance) \
#         .filter(model.UserScholarBalance.user_id == user_id).first()
#     balance = user_scholar_balance.balance
#
#     return render_template('product_pay.html',
#                            action='create',
#                            service=service_template,
#                            balance=balance,
#                            title='支付')


app.add_url_rule('/product/renew/pay/<service_id>',
                 view_func=views.RenewProductView.as_view('renew_product'))
# @app.route('/product/renew/pay/<service_id>')
# def renew_product(service_id):
#     # 防止当前登录用户续费不属于自己的套餐
#     user_id = derive_user_id_from_session()
#     db_session = derive_db_session()
#
#     user_service = db_session.query(model.UserService) \
#         .filter(model.Service.id == service_id) \
#         .filter(model.UserService.service_id == model.Service.id) \
#         .filter(model.UserService.user_id == user_id).first()
#     if user_service is None:
#         return redirect(url_for('product'))
#
#     service = db_session.query(model.Service).filter(model.Service.id == service_id).first()
#
#     service_template = db_session.query(model.ServiceTemplate) \
#         .filter(model.ServiceTemplate.id == service.template_id).first()
#     if service_template is None:
#         return abort(404)
#     service_template.descriptions = service_template.description.split('#')
#     service_template.total_price = service_template.price
#
#     user_scholar_balance = db_session.query(model.UserScholarBalance) \
#         .filter(model.UserScholarBalance.user_id == user_id).first()
#     balance = user_scholar_balance.balance
#
#     return render_template('product_pay.html',
#                            action='renew',
#                            service=service_template,
#                            balance=balance,
#                            title='续费')


app.add_url_rule('/agreement/', view_func=views.BaseView.as_view('agreement', 'agreement.html', '用户协议'))


# -------------------------------------------------- API -------------------------------------------------- #
# -------------------------------------------------- API -------------------------------------------------- #
# -------------------------------------------------- API -------------------------------------------------- #
# -------------------------------------------------- API -------------------------------------------------- #
# -------------------------------------------------- API -------------------------------------------------- #


app.add_url_rule('/api/today_in_history', view_func=method_views.TodayInHistoryAPI.as_view('api_today_in_history'))
app.add_url_rule('/api/login', view_func=method_views.LoginAPI.as_view('api_login'))
app.add_url_rule('/api/register', view_func=method_views.RegisterAPI.as_view('api_register'))
app.add_url_rule('/api/user', view_func=method_views.UserAPI.as_view('api_user'))
app.add_url_rule('/api/invitation', view_func=method_views.InvitationCodeAPI.as_view('api_invitation'))
app.add_url_rule('/api/permission', view_func=method_views.PermissionAPI.as_view('api_permission'))
app.add_url_rule('/api/event', view_func=method_views.EventAPI.as_view('api_event'))
app.add_url_rule('/api/role', view_func=method_views.RoleAPI.as_view('api_role'))
app.add_url_rule('/api/service-template', view_func=method_views.ServiceTemplateAPI.as_view('api_service_template'))
app.add_url_rule('/api/service', view_func=method_views.ServiceAPI.as_view('api_service'))
app.add_url_rule('/api/usage', view_func=method_views.UserAPI.as_view('api_usage'))
app.add_url_rule('/api/scholar-balance', view_func=method_views.ScholarBalanceAPI.as_view('api_scholar_balance'))
app.add_url_rule('/api/service-password', view_func=method_views.ServicePasswordAPI.as_view('api_service_password'))


if __name__ == '__main__':
    create_app()
    # create_app('configs.ProductionConfig')
    host = app.config['HOST']
    port = app.config['PORT']
    processes = app.config['PROCESSES']

    app.run(host=host, port=port, processes=processes)
