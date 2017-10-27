import datetime
import hashlib
import random
import re
import time
import urllib.request

import markdown2
import sqlalchemy
from flask import Flask, redirect, url_for, render_template, json, session, request, abort, make_response
from flask.json import jsonify
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import init_app
import model
import permission
import exception.http
import exception.api
from server import shadowsocks_controller
from util import date_util

app = Flask(__name__)
app.config.from_object('configs.Config')

# _SESSION_KEY = app.config['SECRET_KEY']
_SHA1_PASSWORD_SALT = app.config['SHA1_SALT']
__ITEM_PER_PAGE = app.config['ITEM_PER_PAGE']
_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

Session(app)

db = SQLAlchemy(app)
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])


def derive_db_session(pagination=False):
    if pagination:
        return db.session
    else:
        return sessionmaker(bind=engine)()


def derive_user_id_from_session(call_by_api=False):
    if call_by_api:
        permission.check_user_api_permission()
    else:
        permission.check_user_permission()
    return session['user']['id']


def create_app(config='configs.DevelopmentConfig'):
    """
    生成app实例
    :param config: 'configs.DevelopmentConfig' or 'configs.ProductionConfig'
    :return:
    """
    # app.config.from_object('configs.DevelopmentConfig')
    # app.config.from_object('configs.ProductionConfig')
    app.config.from_object(config)

    init_app.init_jinja2()
    init_app.init_jinja2_global(app)

    global engine
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    return app


# -------------------------------------------------- Error Handler -------------------------------------------------- #
# -------------------------------------------------- Error Handler -------------------------------------------------- #
# -------------------------------------------------- Error Handler -------------------------------------------------- #
# -------------------------------------------------- Error Handler -------------------------------------------------- #
# -------------------------------------------------- Error Handler -------------------------------------------------- #

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


@app.route('/')
def home_page():
    permission.check_user_permission()

    return render_template('index.html',
                           title='主页')


@app.route('/index/')
def index():
    return redirect(url_for('home_page'))


@app.route('/login/')
def login():
    return render_template('login.html',
                           title='登录')


@app.route('/register/')
def register():
    return render_template('register.html',
                           title='注册')


@app.route('/logout/')
def logout():
    session.pop('user', None)
    return redirect(url_for('home_page'))


@app.route('/manage/')
def manage():
    if not permission.check_manage_permission(derive_db_session(), derive_user_id_from_session()):
        return redirect(url_for('home_page'))

    return render_template('manage.html',
                           title='后台管理')


@app.route('/manage/invitation/')
def manage_invitation():
    db_session = derive_db_session(pagination=True)
    if not permission.check_manage_invitation_code_permission(db_session, derive_user_id_from_session()):
        raise exception.http.Forbidden()

    page = request.args.get('page')
    try:
        page = int(page) if page is not None else 1
    except ValueError:
        return redirect(url_for('manage_invitation'))

    pagination = db_session.query(model.InvitationCode).order_by(model.InvitationCode.created_at.desc()).paginate(
        page, __ITEM_PER_PAGE, False)
    if page > 1 and len(pagination.items) is 0:
        return redirect(url_for('manage_invitation'))
    else:
        for invitation in pagination.items:
            inviter = db_session.query(model.User).filter_by(id=invitation.inviter_id).first()
            invitation.inviter_username = inviter.username
            if invitation.invitee_id is not None:
                invitee = db_session.query(model.User).filter_by(id=invitation.invitee_id).first()
                invitation.invitee_username = invitee.username

    return render_template('manage_invitation.html',
                           title='邀请码管理',
                           pagination=pagination,
                           pagination_url_for='manage_invitation')


@app.route('/manage/role/')
def manage_role():
    db_session = derive_db_session(pagination=True)
    if not permission.check_manage_role_permission(db_session, derive_user_id_from_session()):
        raise exception.http.Forbidden()

    page = request.args.get('page')
    try:
        page = int(page) if page is not None else 1
    except ValueError:
        return redirect(url_for('manage_role'))

    pagination = db_session.query(model.Role).order_by(model.Role.id).paginate(
        page, __ITEM_PER_PAGE, False)
    if page > 1 and len(pagination.items) is 0:
        return redirect(url_for('manage_role'))

    return render_template('manage_role.html',
                           title='角色管理',
                           pagination=pagination,
                           pagination_url_for='manage_role')


@app.route('/manage/role/create/')
def create_role():
    if not permission.check_manage_role_permission(derive_db_session(), derive_user_id_from_session()):
        return redirect(url_for('home_page'))

    return render_template('manage_role_edit.html',
                           title='创建角色',
                           action='POST')


@app.route('/manage/role/edit/')
def edit_role():
    if not permission.check_manage_role_permission(derive_db_session(), derive_user_id_from_session()):
        return redirect(url_for('home_page'))

    role_id = request.args.get('id')
    return render_template('manage_role_edit.html',
                           title='编辑角色',
                           id=role_id,
                           action='PATCH')


@app.route('/manage/service-template/')
def manage_service_template():
    db_session = derive_db_session(pagination=True)
    if not permission.check_manage_service_template_permission(db_session, derive_user_id_from_session()):
        raise exception.http.Forbidden()

    page = request.args.get('page')
    try:
        page = int(page) if page is not None else 1
    except ValueError:
        return redirect(url_for('manage_service_template'))

    pagination = db_session.query(model.ServiceTemplate).order_by(model.ServiceTemplate.id).paginate(
        page, __ITEM_PER_PAGE, False)
    if page > 1 and len(pagination.items) is 0:
        return redirect(url_for('manage_service_template'))

    return render_template('manage_service_template.html',
                           title='套餐模版管理',
                           pagination=pagination,
                           pagination_url_for='manage_service_template')


@app.route('/manage/service-template/create/')
def create_service_template():
    if not permission.check_manage_service_template_permission(derive_db_session(), derive_user_id_from_session()):
        raise exception.http.Forbidden()

    service_type = request.args.get('type') if request.args.get('type') else 0

    return render_template('manage_service_template_edit.html',
                           title='创建套餐',
                           type=service_type,
                           action='POST')


@app.route('/manage/service-template/edit/')
def edit_service_template():
    if not permission.check_manage_service_template_permission(derive_db_session(), derive_user_id_from_session()):
        raise exception.http.Forbidden()

    service_template_id = request.args.get('id')

    return render_template('manage_service_template_edit.html',
                           title='编辑套餐',
                           id=service_template_id,
                           action='PATCH')


@app.route('/manage/event/')
def manage_event():
    db_session = derive_db_session(pagination=True)
    if not permission.check_manage_event_permission(db_session, derive_user_id_from_session()):
        raise exception.http.Forbidden()

    page = request.args.get('page')
    try:
        page = int(page) if page is not None else 1
    except ValueError:
        return redirect(url_for('manage_event'))

    pagination = db_session.query(model.Event).order_by(model.Event.created_at.desc()).paginate(
        page, __ITEM_PER_PAGE, False)
    if page > 1 and len(pagination.items) is 0:
        return redirect(url_for('manage_event'))
    else:
        for product in pagination.items:
            user = db_session.query(model.User).filter_by(id=product.user_id).first()
            product.user_name = user.name

    return render_template('manage_event.html',
                           title='公告管理',
                           pagination=pagination,
                           pagination_url_for='manage_event')


@app.route('/manage/event/create/')
def create_event():
    if not permission.check_manage_event_permission(derive_db_session(), derive_user_id_from_session()):
        return redirect(url_for('home_page'))

    return render_template('manage_event_edit.html',
                           title='发布公告',
                           action='POST')


@app.route('/manage/event/edit/')
def edit_event():
    if not permission.check_manage_event_permission(derive_db_session(), derive_user_id_from_session()):
        return redirect(url_for('home_page'))

    product_id = request.args.get('id')
    return render_template('manage_event_edit.html',
                           title='编辑公告',
                           id=product_id,
                           action='PATCH')


@app.route('/manage/user/')
def manage_user():
    db_session = derive_db_session(pagination=True)
    if not permission.check_manage_user_permission(db_session, derive_user_id_from_session()):
        return redirect(url_for('home_page'))

    url = url_for('manage_user')
    page = request.args.get('page')
    try:
        page = int(page) if page is not None else 1
    except ValueError as e:
        return redirect(url)

    pagination = db_session.query(model.User).order_by(model.User.created_at).paginate(
        page, __ITEM_PER_PAGE, False)
    if page > 1 and len(pagination.items) is 0:
        return redirect(url)

    return render_template('manage_user.html',
                           title='用户管理',
                           pagination=pagination,
                           pagination_url_for='manage_user')


@app.route('/user/<name>')
def show_user_profile(name):
    permission.check_user_permission()

    db_session = derive_db_session()
    user = db_session.query(model.User).filter_by(name=name).first()
    if user is None:
        return abort(404)

    return render_template('user.html',
                           title='用户' + name,
                           user=user)


@app.route('/event/')
def event():
    permission.check_user_permission()

    page = request.args.get('page')
    try:
        page = int(page) if page is not None else 1
    except ValueError as e:
        return redirect(url_for('event'))

    db_session = derive_db_session(pagination=True)
    pagination = db_session.query(model.Event).order_by(model.Event.created_at.desc()).paginate(
        page, __ITEM_PER_PAGE, False
    )
    if page > 1 and len(pagination.items) is 0:
        return redirect(url_for('event'))

    for evenet in pagination.items:
        user = db_session.query(model.User).filter_by(id=evenet.user_id).first()
        evenet.user_name = user.name
        evenet.user_image = user.image

    return render_template('event.html',
                           title='公告',
                           pagination=pagination,
                           pagination_url_for='event')


@app.route('/event/<int:event_id>')
def show_event(event_id):
    permission.check_user_permission()

    db_session = derive_db_session()
    event = db_session.query(model.Event).filter_by(id=event_id).first()
    if event is None:
        return abort(404)

    user = db_session.query(model.User).filter_by(id=event.user_id).first()

    event.html_content = markdown2.markdown(event.content, extras=['fenced-code-blocks', 'tables', 'toc'])

    event.html_content = event.html_content.replace('{{ image }}', app.config['URL_OF_BLOG_IMAGE'])

    event.tags = event.tag.split(' ')
    event.user_name = user.name
    event.user_image = user.image

    return render_template('event_view.html',
                           title='公告',
                           event=event)


@app.route('/product/create/')
def create_product():
    permission.check_user_permission()

    db_session = derive_db_session()

    monthly_services = db_session.query(model.ServiceTemplate) \
        .filter(model.ServiceTemplate.type == model.ServiceTemplate.MONTHLY) \
        .all()
    for s in monthly_services:
        s.descriptions = s.description.split('#')

    data_services = db_session.query(model.ServiceTemplate) \
        .filter(model.ServiceTemplate.type == model.ServiceTemplate.DATA) \
        .all()
    for s in data_services:
        s.descriptions = s.description.split('#')

    return render_template('product_create.html',
                           monthly_services=monthly_services,
                           data_services=data_services,
                           title='获取新学术')


@app.route('/product/create/pay/<service_template_id>')
def pay_product(service_template_id):
    permission.check_user_permission()

    db_session = derive_db_session()
    service_template = db_session.query(model.ServiceTemplate) \
        .filter(model.ServiceTemplate.id == service_template_id).first()
    if service_template is None:
        return abort(404)
    service_template.descriptions = service_template.description.split('#')
    service_template.total_price = service_template.price + service_template.initialization_fee

    return render_template('product_create_pay.html',
                           service=service_template,
                           title='支付')


@app.route('/agreement/')
def agreement():
    return render_template('agreement.html',
                           title='用户协议')


# -------------------------------------------------- API -------------------------------------------------- #
# -------------------------------------------------- API -------------------------------------------------- #
# -------------------------------------------------- API -------------------------------------------------- #
# -------------------------------------------------- API -------------------------------------------------- #
# -------------------------------------------------- API -------------------------------------------------- #


@app.route('/api/today_in_history')
def today_in_history_api():
    api_url = 'http://www.ipip5.com/today/api.php?type=json'

    request = urllib.request.Request(api_url)
    response = urllib.request.urlopen(request).read()

    return make_response(jsonify(json.loads(response)), 200)


@app.route('/api/login', methods=['GET', 'POST'])
def api_login():
    if request.method == 'GET':
        return login_api_document()
    elif request.method == 'POST':
        return api_do_login()


def api_do_login():
    name = request.json['name']
    password = request.json['password']
    db_session = derive_db_session()
    if name is not None:
        user = db_session.query(model.User).filter_by(username=name).first()
        if user is None:
            user = db_session.query(model.User).filter_by(email=name).first()
            if user is None:
                return login_api_document('用户不存在', 400)

    else:
        return login_api_document('请输入用户名或邮箱', 400)

    # 检查密码
    sha1 = hashlib.sha1()
    sha1.update(_SHA1_PASSWORD_SALT.encode('utf-8'))
    sha1.update(b':')
    sha1.update(password.encode('utf-8'))
    if user.password != sha1.hexdigest():
        return login_api_document('密码错误，请重试', 400)

    if not permission.check_login_permission(db_session, user.id):
        user_role = db_session.query(model.UserRole).filter(model.UserRole.user_id == user.id).first()
        if user_role is None:
            user_role = model.UserRole(user.id, model.Role.USER)
            try:
                db_session.add(user_role)
                db_session.commit()
            except sqlalchemy.exc.DataError as e:
                db_session.rollback()
                return login_api_document('服务器内部错误，请稍后再试', 500)
        else:
            return login_api_document('该用户已被关进小黑屋，请联系管理员进行申诉', 403)

    user.last_login_at = time.time()

    try:
        db_session.commit()
        session['user'] = model.to_dict(user)
    except sqlalchemy.exc.DataError as e:
        db_session.rollback()
        return abort(make_response(str(e), 500))
    finally:
        db_session.close()

    return make_response(jsonify({
        'message': '登录成功',
        'documentation_url': __LOGIN_API_DOCUMENTATION_URL
    }), 200)


# TODO 文档链接
__LOGIN_API_DOCUMENTATION_URL = 'coming soon...'


def login_api_document(message='', code=400):
    msg = jsonify({
        'message': message,
        'documentation_url': __LOGIN_API_DOCUMENTATION_URL
    })
    return make_response(msg, code)


@app.route('/api/register', methods=['GET', 'POST'])
def api_register():
    if request.method == 'GET':
        return register_api_document()
    elif request.method == 'POST':
        return api_create_user()


# TODO 文档链接
__REGISTER_API_DOCUMENTATION_URL = 'coming soon...'


def register_api_document(message='', code=400):
    msg = jsonify({
        'message': message,
        'documentation_url': __REGISTER_API_DOCUMENTATION_URL
    })
    return make_response(msg, code)


def api_create_user():
    username = request.json['name']
    email = request.json['email']
    password = request.json['password']
    code = request.json['invitation_code']

    if not username or not username.strip():
        return register_api_document('请输入用户名', 400)
    if not email or not _RE_EMAIL.match(email):
        return register_api_document('请输入正确的邮箱', 400)
    if not password or not _RE_SHA1.match(password):
        return register_api_document('请输入符合规则的密码', 400)

    db_session = derive_db_session()
    users = db_session.query(model.User).filter_by(username=username).all()
    if users is not None and len(users) > 0:
        return register_api_document('用户名已经存在', 400)
    users = db_session.query(model.User).filter_by(email=email).all()
    if users is not None and len(users) > 0:
        return register_api_document('邮箱已被注册', 400)

    invitation_code = db_session.query(model.InvitationCode).filter_by(code=code).first()
    if invitation_code is None:
        return register_api_document('邀请码不存在', 400)
    elif not invitation_code.available:
        return register_api_document('邀请码已被使用', 400)

    # 将记录写入user表
    sha1_password = '%s:%s' % (_SHA1_PASSWORD_SALT, password)
    user = model.User(username=username.strip(), email=email, name=username.strip(),
                      password=hashlib.sha1(sha1_password.encode('utf-8')).hexdigest(),
                      image='https://api.adorable.io/avatars/285/%s.png' % hashlib.md5(
                          email.encode('utf-8')).hexdigest())

    try:
        db_session.add(user)
        db_session.commit()
        session['user'] = model.to_dict(user)
    except sqlalchemy.exc.DataError as e:
        db_session.rollback()
        return abort(make_response(str(e), 500))

    # 将记录写入user_role表
    user = db_session.query(model.User).filter_by(username=username).first()

    user_role = model.UserRole(user.id, model.Role.USER)
    db_session.add(user_role)
    # try:
    #     db_session.add(user_role)
    #     db_session.commit()
    # except sqlalchemy.exc.DataError as e:
    #     db_session.rollback()
    #     return abort(make_response(str(e), 500))

    # 将记录写入invitation_code表
    invitation_code.available = False
    invitation_code.invitee_id = user.id
    invitation_code.invited_at = time.time()
    try:
        db_session.commit()
    except sqlalchemy.exc.DataError as e:
        db_session.rollback()
        return abort(make_response(str(e), 500))
    finally:
        db_session.close()

    return make_response(jsonify({
        'message': '注册成功',
        'documentation_url': __REGISTER_API_DOCUMENTATION_URL
    }), 200)


@app.route('/api/user', methods=['GET', 'POST', 'PATCH'])
def api_user():
    if request.method == 'GET':
        return api_get_user()
    elif request.method == 'POST':
        return invitation_code_api_document()
    elif request.method == 'PATCH':
        return api_update_user()
    else:
        return user_api_document()


# TODO 文档链接
__USER_API_DOCUMENTATION_URL = 'coming soon...'


def user_api_document(message='', code=400):
    msg = jsonify({
        'message': message,
        'documentation_url': __USER_API_DOCUMENTATION_URL
    })
    return make_response(msg, code)


def api_get_user():
    pass


def api_update_user():
    # TODO OAUTH
    current_user_id = derive_user_id_from_session(True)

    db_session = derive_db_session()
    permission.check_manage_role_permission(db_session, current_user_id)

    user_id = request.json['user_id']
    if user_id is None:
        return role_api_document('Need user_id field')
    role_id = request.json['role_id']
    if role_id is None:
        return role_api_document('Need role_id field')

    user_role = db_session.query(model.UserRole) \
        .filter(model.User.id == model.UserRole.user_id) \
        .filter(model.UserRole.role_id == model.Role.id) \
        .filter(model.User.id == user_id).first()

    user_role.role_id = role_id

    try:
        db_session.commit()
    except sqlalchemy.exc.DataError as e:
        db_session.rollback()
        return abort(make_response(str(e), 500))
    finally:
        db_session.close()

    return make_response(jsonify({
        'message': '修改用户角色成功',
        'documentation_url': __USER_API_DOCUMENTATION_URL
    }), 201)


@app.route('/api/invitation', methods=['GET', 'POST', 'DELETE'])
def api_invitation_code():
    if request.method == 'GET':
        return api_get_invitation_code()
    elif request.method == 'POST':
        return api_create_invitation_code()
    elif request.method == 'DELETE':
        return api_delete_invitation_code()
    else:
        return invitation_code_api_document()


# TODO 文档链接
__INVITATION_CODE_API_DOCUMENTATION_URL = 'coming soon...'


def invitation_code_api_document(message='', code=400):
    msg = jsonify({
        'message': message,
        'documentation_url': __INVITATION_CODE_API_DOCUMENTATION_URL
    })
    return make_response(msg, code)


def api_get_invitation_code():
    pass


def api_create_invitation_code():
    # TODO OAUTH
    user_id = derive_user_id_from_session(True)
    db_session = derive_db_session()
    if user_id is None:
        return invitation_code_api_document('Need user_id')
    if not permission.check_manage_invitation_code_permission(db_session, user_id, True):
        raise exception.api.Forbidden('ID为%s的用户无权创建邀请码' % user_id)

    invitation_code = None
    invitation = 1
    while invitation is not None:
        invitation_code = derive_invitation_code()
        invitation = db_session.query(model.InvitationCode) \
            .filter(model.InvitationCode.code == invitation_code).first()

    invitation = model.InvitationCode(invitation_code, user_id)

    try:
        db_session.add(invitation)
        db_session.commit()
    except sqlalchemy.exc.DataError as e:
        db_session.rollback()
        return abort(make_response(str(e), 500))
    finally:
        db_session.close()

    return make_response(jsonify({
        'message': '生成邀请码成功',
        'code': invitation_code,
        'documentation_url': __INVITATION_CODE_API_DOCUMENTATION_URL
    }), 201)


def api_delete_invitation_code():
    pass


def derive_invitation_code():
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+=-"
    codes = []
    for i in range(32):
        codes.append(random.choice(seed))
    invitation_code = ''.join(codes)
    return invitation_code


@app.route('/api/permission', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def api_permission():
    if request.method == 'GET':
        return api_get_permission()
    elif request.method == 'POST':
        return permission_api_document()
    elif request.method == 'PUT':
        return permission_api_document()
    elif request.method == 'PATCH':
        return permission_api_document()
    elif request.method == 'DELETE':
        return permission_api_document()


# TODO 文档链接
__PERMISSION_API_DOCUMENTATION_URL = 'coming soon...'


def permission_api_document(message='', code=400):
    msg = jsonify({
        'message': message,
        'documentation_url': __PERMISSION_API_DOCUMENTATION_URL
    })
    return make_response(msg, code)


def api_get_permission():
    # TODO OAUTH
    db_session = derive_db_session()
    user_id = derive_user_id_from_session(True)

    query_user_id = request.args.get('user_id')
    query_role_id = request.args.get('role_id')
    return_all_permissions = request.args.get('all_permissions')

    all_permission_list = []
    if (query_user_id is None and query_role_id is None) or return_all_permissions:
        all_permissions = db_session.query(model.Permission).all()
        for p in all_permissions:
            all_permission_list.append(model.to_dict(p))

        if query_user_id is None and query_role_id is None:
            return make_response(
                jsonify({
                    'all_permissions': all_permission_list
                })
            )

    data = None
    if query_user_id is not None:
        if not permission.check_manage_user_permission(db_session, user_id):
            return permission_api_document('ID为%s的用户无权进行用户管理' % user_id)

        permissions = permission.derive_user_permissions(derive_db_session(), user_id)
        permission_list = []
        for p in permissions:
            permission_list.append(model.to_dict(p))

        data = {
            'user_id': user_id,
            'permissions': permission_list
        }

    elif query_role_id is not None:
        if not permission.check_manage_role_permission(db_session, user_id):
            return permission_api_document('ID为%s的用户无权进行角色管理' % user_id)

        role = db_session.query(model.Role).filter(model.Role.id == query_role_id).first()

        permissions = db_session.query(model.Permission) \
            .filter(model.Role.id == model.RolePermission.role_id) \
            .filter(model.RolePermission.permission_id == model.Permission.id) \
            .filter(model.Role.id == query_role_id)
        permission_list = []
        for p in permissions:
            permission_list.append(model.to_dict(p))
        data = {
            'role_id': query_role_id,
            'role_name': role.name,
            'role_label': role.label,
            'role_description': role.description,
            'permissions': permission_list
        }

    if return_all_permissions:
        data['all_permissions'] = all_permission_list

    return make_response(jsonify(data), 200)


@app.route('/api/event', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def event_api():
    if request.method == 'GET':
        return api_get_event()
    elif request.method == 'POST':
        return api_create_event()
    elif request.method == 'PATCH':
        return api_update_event()
    elif request.method == 'DELETE':
        return api_delete_event()


# TODO 文档链接
__EVENT_API_DOCUMENTATION_URL = 'coming soon...'


def event_api_document(message='', code=400):
    msg = jsonify({
        'message': message,
        'documentation_url': __EVENT_API_DOCUMENTATION_URL
    })
    return make_response(msg, code)


def api_get_event():
    event_id = request.args.get('id')
    if event_id is None:
        return event_api_document()

    db_session = derive_db_session()
    event = db_session.query(model.Event).filter_by(id=event_id).first()
    if event is None:
        return event_api_document('id为%s的公告不存在' % event_id, 404)

    data = model.to_dict(event)

    html_version = request.args.get('html')
    if html_version:
        html_content = markdown2.markdown(event.content, extras=['fenced-code-blocks', 'tables', 'toc'])
        html_content = html_content.replace('{{ image }}', app.config['URL_OF_BLOG_IMAGE'])
        data['html'] = html_content

    return make_response(
        jsonify({
            'message': '获取公告成功',
            'event': data,
            'documentation_url': __EVENT_API_DOCUMENTATION_URL
        }), 200
    )


def api_create_event():
    # TODO OAUTH
    user_id = derive_user_id_from_session(True)
    db_session = derive_db_session()
    if user_id is None:
        return event_api_document('Need user_id')
    if not permission.check_manage_event_permission(db_session, user_id):
        raise exception.api.Forbidden('ID为%s的用户无权创建公告' % user_id)

    name = request.json['name']
    tag = request.json['tag']
    summary = request.json['summary']
    content = request.json['content']

    if not name or not name.strip():
        return event_api_document('公告名字不能为空', 400)
    if not summary or not summary.strip():
        return event_api_document('公告描述不能为空', 400)
    if not content or not content.strip():
        return event_api_document('公告内容不能为空', 400)

    event = model.Event(user_id=user_id, name=name.strip(), tag=tag, summary=summary.strip(),
                        content=content.strip())
    try:
        db_session.add(event)
        db_session.commit()
    except sqlalchemy.exc.DataError as e:
        db_session.rollback()
        return abort(make_response(str(e), 500))
    finally:
        db_session.close()

    return make_response(
        jsonify({
            'message': '发布公告成功',
            'documentation_url': __EVENT_API_DOCUMENTATION_URL
        }), 201
    )


def api_update_event():
    # TODO OAUTH
    user_id = derive_user_id_from_session(True)
    db_session = derive_db_session()
    if user_id is None:
        return event_api_document('Need user_id')
    if not permission.check_manage_event_permission(db_session, user_id):
        raise exception.api.Forbidden('ID为%s的用户无权编辑公告' % user_id)

    id = request.json['id']
    name = request.json['name']
    tag = request.json['tag']
    summary = request.json['summary']
    content = request.json['content']

    if not name or not name.strip():
        return event_api_document('公告名字不能为空', 400)
    if not summary or not summary.strip():
        return event_api_document('公告描述不能为空', 400)
    if not content or not content.strip():
        return event_api_document('公告内容不能为空', 400)

    db_session.query(model.Event).filter_by(id=id).update({
        'name': name,
        'tag': tag,
        'summary': summary,
        'content': content
    })

    try:
        db_session.commit()
    except sqlalchemy.exc.DataError as e:
        db_session.rollback()
        return abort(make_response(str(e), 500))
    finally:
        db_session.close()

    return make_response(
        jsonify({
            'message': '修改公告成功',
            'documentation_url': __EVENT_API_DOCUMENTATION_URL
        }), 201
    )


def api_delete_event():
    """
    删除公告
    :return:
    """
    # TODO OAUTH
    user_id = derive_user_id_from_session(True)
    db_session = derive_db_session()
    if not permission.check_manage_event_permission(db_session, user_id):
        raise exception.api.Forbidden('ID为%s的用户无权删除公告' % user_id)

    product_id = request.json['id']
    if not product_id:
        return event_api_document('所需删除的公告id不能为空', 400)

    product = db_session.query(model.Event).filter_by(id=product_id).first()
    if not product:
        return event_api_document('id为%s公告不存在，故无法删除' % product_id, 404)

    try:
        db_session.delete(product)
        db_session.commit()
    except sqlalchemy.exc.DataError as e:
        db_session.rollback()
        return abort(make_response(str(e), 500))
    finally:
        db_session.close()

    return make_response(
        jsonify({
            'message': '删除公告成功',
            'documentation_url': __EVENT_API_DOCUMENTATION_URL
        }), 204
    )


@app.route('/api/role', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def role_api():
    if request.method == 'GET':
        return api_get_role()
    elif request.method == 'POST':
        return api_create_role()
    elif request.method == 'PATCH':
        return api_update_role()
    elif request.method == 'DELETE':
        return api_delete_role()


# TODO 文档链接
__ROLE_API_DOCUMENTATION_URL = 'coming soon...'


def role_api_document(message='', code=400):
    msg = jsonify({
        'message': message,
        'documentation_url': __ROLE_API_DOCUMENTATION_URL
    })
    return make_response(msg, code)


def api_get_role():
    # TODO OAUTH
    current_user_id = derive_user_id_from_session(True)

    db_session = derive_db_session()
    permission.check_manage_role_permission(db_session, current_user_id)

    # 查询用户当前角色
    user_role = None
    user_id = request.args.get('user_id')
    if user_id is not None:
        user_role = db_session.query(model.Role) \
            .filter(model.User.id == model.UserRole.user_id) \
            .filter(model.UserRole.role_id == model.Role.id) \
            .filter(model.User.id == user_id).first()

    # 查询所有角色列表
    roles = db_session.query(model.Role).order_by(model.Role.id).all()

    role_list = []
    for role in roles:
        role_list.append(model.to_dict(role))

    result = {
        'documentation_url': __ROLE_API_DOCUMENTATION_URL,
        'roles': role_list
    }
    if user_role is not None:
        result['user_role'] = model.to_dict(user_role)

    return make_response(jsonify(result), 200)


def api_create_role():
    # TODO OAUTH
    current_user_id = derive_user_id_from_session(True)

    db_session = derive_db_session()
    permission.check_manage_role_permission(db_session, current_user_id)

    name = request.json['name']
    if name is None:
        return role_api_document('Need name field')
    label = request.json['label']
    if label is None:
        return role_api_document('Need label field')
    description = request.json['description']
    # if description is None:
    #     return role_api_document('Need description field')
    permissions = request.json['permissions']
    # if permissions is None:
    #     return role_api_document('Need permissions field')

    role = model.Role(name, label, description)
    try:
        db_session.add(role)
        db_session.commit()
    except sqlalchemy.exc.DataError as e:
        db_session.rollback()
        return abort(make_response(str(e), 500))
    finally:
        db_session.close()

    role = db_session.query(model.Role).filter(model.Role.name == name).first()
    role_id = role.id

    for permission_id in permissions:
        role_permission = model.RolePermission(role_id, permission_id)
        db_session.add(role_permission)

    try:
        db_session.commit()
    except sqlalchemy.exc.DataError as e:
        db_session.rollback()
        return abort(make_response(str(e), 500))
    finally:
        db_session.close()

    return make_response(
        jsonify({
            'message': '创建角色成功',
            'role_id': role_id,
            'documentation_url': __ROLE_API_DOCUMENTATION_URL
        }), 201
    )


def api_update_role():
    # TODO OAUTH
    user_id = derive_user_id_from_session(True)

    db_session = derive_db_session()
    permission.check_manage_role_permission(db_session, user_id)

    role_id = request.json['id']
    if role_id is None:
        return role_api_document('Need id field')
    name = request.json['name']
    if name is None:
        return role_api_document('Need name field')
    label = request.json['label']
    if label is None:
        return role_api_document('Need label field')
    description = request.json['description']
    # if description is None:
    #     return role_api_document('Need description field')
    permissions = request.json['permissions']
    # if permissions is None:
    #     return role_api_document('Need permissions field')

    # 更新role表
    db_session.query(model.Role).filter(model.Role.id == role_id).update({
        'name': name,
        'label': label,
        'description': description
    })

    # try:
    #     db_session.commit()
    # except sqlalchemy.exc.DataError as e:
    #     db_session.rollback()
    #     return abort(make_response(str(e), 500))
    # finally:
    #     db_session.close()

    # 删除role_permission表的旧记录
    role_permissions = db_session.query(model.RolePermission) \
        .filter(model.Role.id == model.RolePermission.role_id) \
        .filter(model.Role.id == role_id).all()

    for role_permission in role_permissions:
        db_session.delete(role_permission)

    # try:
    #     db_session.commit()
    # except sqlalchemy.exc.DataError as e:
    #     db_session.rollback()
    #     return abort(make_response(str(e), 500))
    # finally:
    #     db_session.close()

    # 新增角色权限记录到role_permission表
    for permission_id in permissions:
        role_permission = model.RolePermission(role_id, permission_id)
        db_session.add(role_permission)

    try:
        db_session.commit()
    except sqlalchemy.exc.DataError as e:
        db_session.rollback()
        return abort(make_response(str(e), 500))
    finally:
        db_session.close()

    return make_response(
        jsonify({
            'message': '更新角色成功',
            'role_id': role_id,
            'documentation_url': __ROLE_API_DOCUMENTATION_URL
        }), 201
    )


def api_delete_role():
    # TODO OAUTH
    user_id = derive_user_id_from_session(True)
    db_session = derive_db_session()
    if not permission.check_manage_event_permission(db_session, user_id):
        raise exception.api.Forbidden('ID为%s的用户无权删除角色' % user_id)

    role_id = request.json['id']
    if not role_id:
        return role_api_document('所需删除的角色id不能为空', 400)

    # 判断是否有user的角色是待删除角色
    users = db_session.query(model.User) \
        .filter(model.UserRole.user_id == model.User.id) \
        .filter(model.UserRole.role_id == model.Role.id) \
        .filter(model.Role.id == role_id).all()

    if users is not None and len(users) > 0:
        raise exception.api.InvalidRequest('当前还有%s位用户的角色为待删除角色，故无法删除该角色' % len(users))

    # 从role_permission表删除记录
    role_permissions = db_session.query(model.RolePermission) \
        .filter(model.Role.id == role_id) \
        .filter(model.Role.id == model.RolePermission.role_id).all()
    for role_permission in role_permissions:
        db_session.delete(role_permission)

    # 从role表删除记录
    role = db_session.query(model.Role).filter_by(id=role_id).first()
    if not role:
        return role_api_document('id为%s公告不存在，故无法删除' % role_id, 404)

    try:
        db_session.delete(role)
        db_session.commit()
    except sqlalchemy.exc.DataError as e:
        db_session.rollback()
        return abort(make_response(str(e), 500))
    finally:
        db_session.close()

    return make_response(
        jsonify({
            'message': '删除角色成功',
            'documentation_url': __ROLE_API_DOCUMENTATION_URL
        }), 204
    )


@app.route('/api/service-template', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def service_template_api():
    if request.method == 'GET':
        return api_get_service_template()
    elif request.method == 'POST':
        return api_create_service_template()
    elif request.method == 'PATCH':
        return api_update_service_template()
    elif request.method == 'DELETE':
        return api_delete_service_template()


# TODO 文档链接
__SERVICE_TEMPLATE_API_DOCUMENTATION_URL = 'coming soon...'


def service_template_api_document(message='', code=400):
    msg = jsonify({
        'message': message,
        'documentation_url': __SERVICE_TEMPLATE_API_DOCUMENTATION_URL
    })
    return make_response(msg, code)


def api_get_service_template():
    service_template_id = request.args.get('id')
    if service_template_id is None:
        return service_template_api_document('Need id field.')

    db_session = derive_db_session()

    service_template = db_session.query(model.ServiceTemplate) \
        .filter(model.ServiceTemplate.id == service_template_id).first()

    if service_template is None:
        return service_template_api_document('ID为%s的套餐模板不存在' % service_template_id, 404)

    return make_response(
        jsonify({
            'message': '获取套餐模板成功',
            'template': model.to_dict(service_template),
            'documentation_url': __SERVICE_TEMPLATE_API_DOCUMENTATION_URL
        }), 200
    )


def api_create_service_template():
    # TODO OAUTH2
    user_id = derive_user_id_from_session(True)
    db_session = derive_db_session()
    if not permission.check_manage_service_template_permission(db_session, user_id):
        raise exception.api.Forbidden('ID为%s的用户无权创建套餐模版' % user_id)

    service_type = request.json['type']
    if service_type is None:
        return service_template_api_document('Need type field.')
    title = request.json['title']
    if title is None:
        return service_template_api_document('Need title field.')
    subtitle = request.json['subtitle']
    if subtitle is None:
        return service_template_api_document('Need subtitle field.')
    description = request.json['description']
    if description is None:
        return service_template_api_document('Need description field.')
    balance = request.json['balance']
    if balance is None:
        return service_template_api_document('Need balance field.')
    price = request.json['price']
    if price is None:
        return service_template_api_document('Need price field.')
    initialization_fee = request.json['initialization_fee']
    if initialization_fee is None:
        return service_template_api_document('Need initialization_fee field.')

    service_template = model.ServiceTemplate(service_type, title, subtitle, description, balance, price,
                                             initialization_fee)
    db_session.add(service_template)

    try:
        db_session.commit()
    except sqlalchemy.exc.DataError as e:
        db_session.rollback()
        return abort(make_response(str(e), 500))
    finally:
        db_session.close()

    return make_response(
        jsonify({
            'message': '创建套餐模板成功',
            'documentation_url': __SERVICE_TEMPLATE_API_DOCUMENTATION_URL
        }), 201
    )


def api_update_service_template():
    # TODO OAUTH2
    user_id = derive_user_id_from_session(True)
    db_session = derive_db_session()
    if not permission.check_manage_service_template_permission(db_session, user_id):
        raise exception.api.Forbidden('ID为%s的用户无权创建套餐模版' % user_id)

    service_id = request.json['id']
    if service_id is None:
        return service_template_api_document('Need id field.')
    service_type = request.json['type']
    if service_type is None:
        return service_template_api_document('Need type field.')
    title = request.json['title']
    if title is None:
        return service_template_api_document('Need title field.')
    subtitle = request.json['subtitle']
    if subtitle is None:
        return service_template_api_document('Need subtitle field.')
    description = request.json['description']
    if description is None:
        return service_template_api_document('Need description field.')
    balance = request.json['balance']
    if balance is None:
        return service_template_api_document('Need balance field.')
    price = request.json['price']
    if price is None:
        return service_template_api_document('Need price field.')
    initialization_fee = request.json['initialization_fee']
    if initialization_fee is None:
        return service_template_api_document('Need initialization_fee field.')

    service_template = db_session.query(model.ServiceTemplate).filter(model.ServiceTemplate.id == service_id).first()

    if service_template is None:
        return service_template_api_document('ID为%s的套餐模板不存在' % service_id, 404)

    service_template.type = service_type
    service_template.title = title
    service_template.subtitle = subtitle
    service_template.description = description
    service_template.balance = balance
    service_template.price = price
    service_template.initialization_fee = initialization_fee

    try:
        db_session.commit()
    except sqlalchemy.exc.DataError as e:
        db_session.rollback()
        return abort(make_response(str(e), 500))
    finally:
        db_session.close()

    return make_response(
        jsonify({
            'message': '编辑套餐模板成功',
            'documentation_url': __SERVICE_TEMPLATE_API_DOCUMENTATION_URL
        }), 201
    )


def api_delete_service_template():
    # TODO OAUTH2
    user_id = derive_user_id_from_session(True)
    db_session = derive_db_session()
    if not permission.check_manage_service_template_permission(db_session, user_id):
        raise exception.api.Forbidden('ID为%s的用户无权删除套餐模版' % user_id)

    service_template_id = request.json['id']
    if service_template_id is None:
        return service_template_api_document('Need id field.')

    service_template = db_session.query(model.ServiceTemplate).filter(
        model.ServiceTemplate.id == service_template_id).first()
    db_session.delete(service_template)

    try:
        db_session.commit()
    except sqlalchemy.exc.DataError as e:
        db_session.rollback()
        return abort(make_response(str(e), 500))
    finally:
        db_session.close()

    return make_response(
        jsonify({
            'message': '删除套餐模板成功',
            'documentation_url': __SERVICE_TEMPLATE_API_DOCUMENTATION_URL
        }), 204
    )


@app.route('/api/service', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def service_api():
    if request.method == 'GET':
        return api_get_service()
    elif request.method == 'POST':
        return api_create_service()
    elif request.method == 'PATCH':
        return api_update_service()
    elif request.method == 'DELETE':
        return api_delete_service()
    else:
        return service_api_document()


# TODO 文档链接
__SERVICE_API_DOCUMENTATION_URL = 'coming soon...'


def service_api_document(message='', code=400):
    msg = jsonify({
        'message': message,
        'documentation_url': __SERVICE_API_DOCUMENTATION_URL
    })
    return make_response(msg, code)


def api_get_service():
    pass


def api_create_service():
    permission.check_user_api_permission()

    user_id = derive_user_id_from_session(True)
    service_template_id = request.json['template_id']
    if service_template_id is None:
        return service_api_document('Need service_template_id field.')
    password = request.json['password']
    if password is None:
        return service_api_document('Need password field.')
    db_session = derive_db_session()
    service_template = db_session.query(model.ServiceTemplate) \
        .filter(model.ServiceTemplate.id == service_template_id).first()

    # TODO 扣费系统

    service_type = service_template.type
    now = datetime.datetime.now()
    created_at = now.timestamp()
    last_reset_at = None
    if service_type == model.ServiceTemplate.MONTHLY:
        auto_renew = request.json['auto_renew']
        if auto_renew is None:
            return service_api_document('Need auto_renew field.')
        if auto_renew:
            reset_at = date_util.derive_1st_of_next_month(now)
            expired_at = datetime.datetime(2099, 12, 31, 23, 59, 59).timestamp()
        else:
            reset_at = None
            expired_at = created_at + 365 * 24 * 60 * 60
    elif service_type == model.ServiceTemplate.DATA:
        reset_at = None
        expired_at = created_at + 365 * 24 * 60 * 60
    else:
        reset_at = None
        expired_at = created_at

    service = model.Service(0, service_template.balance, reset_at, last_reset_at, created_at, expired_at, 0)
    db_session.add(service)

    try:
        db_session.commit()
    except sqlalchemy.exc.DataError as e:
        db_session.rollback()
        return abort(make_response(str(e), 500))

    service_id = service.id

    user_service = model.UserService(user_id, service_id)
    db_session.add(user_service)

    service_port = derive_available_shadowsocks_port(db_session)

    service_password = model.ServicePassword(service.id, service_port, password)
    db_session.add(service_password)

    try:
        db_session.commit()
    except sqlalchemy.exc.DataError as e:
        db_session.rollback()
        return abort(make_response(str(e), 500))
    finally:
        db_session.close()

    return make_response(
        jsonify({
            'message': '创建套餐成功',
            'service_id': service_id,
            'documentation_url': __SERVICE_API_DOCUMENTATION_URL
        }), 201
    )


def derive_available_shadowsocks_port(db_session):
    service_passwords = db_session.query(model.ServicePassword) \
        .order_by(model.ServicePassword.port.desc()) \
        .filter(model.Service.available == True) \
        .filter(model.Service.id == model.ServicePassword.service_id).all()

    if service_passwords is None or len(service_passwords) == 0:
        return app.config['SERVICE_MIN_PORT']
    else:
        return service_passwords[0].port


def api_update_service():
    pass


def api_delete_service():
    pass


@app.route('/api/usage', methods=['POST'])
def usage_api():
    data = request.data.decode('utf-8')
    data = data[6:]

    print(data)

    data = json.loads(data)

    for k, v in data.items():
        print('port %s use data: %s' % (k, v))

    return 'OK'


@app.route('/api/ss', methods=['POST'])
def ss_api():
    data = request.data.decode('utf-8')

    print(data)

    return 'OK'


if __name__ == '__main__':
    create_app()
    # create_app('configs.ProductionConfig')
    host = app.config['HOST']
    port = app.config['PORT']
    processes = app.config['PROCESSES']
    app.run(host=host, port=port, processes=processes)
