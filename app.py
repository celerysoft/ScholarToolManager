import hashlib
import urllib

import re

import sqlalchemy
import time
from flask import Flask, redirect, url_for, render_template, json, session, request, abort, make_response
from flask.json import jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy

import exception
import init_app
import model
import permission

app = Flask(__name__)
app.config.from_object('configs.Config')

# _SESSION_KEY = app.config['SECRET_KEY']
_SHA1_PASSWORD_SALT = app.config['SHA1_SALT']
__ITEM_PER_PAGE = app.config['ITEM_PER_PAGE']
_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

Session(app)
init_app.init_jinja2()
init_app.init_jinja2_global(app)

db = SQLAlchemy(app)
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])


def derive_db_session(pagination=False):
    if pagination:
        return db.session
    else:
        return sessionmaker(bind=engine)()


def create_app(config='configs.DevelopmentConfig'):
    """
    生成app实例
    :param config: 'configs.DevelopmentConfig' or 'configs.ProductionConfig'
    :return:
    """
    # app.config.from_object('configs.DevelopmentConfig')
    # app.config.from_object('configs.ProductionConfig')
    app.config.from_object(config)
    global engine
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    return app


# -------------------------------------------------- Error Handler -------------------------------------------------- #
# -------------------------------------------------- Error Handler -------------------------------------------------- #
# -------------------------------------------------- Error Handler -------------------------------------------------- #
# -------------------------------------------------- Error Handler -------------------------------------------------- #
# -------------------------------------------------- Error Handler -------------------------------------------------- #

@app.errorhandler(exception.Unauthorized)
def handle_unauthorized(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    # return response
    return redirect(url_for('login'))


@app.errorhandler(exception.Forbidden)
def handle_unauthorized(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    # return response
    return redirect(url_for('login'))


# -------------------------------------------------- PAGE -------------------------------------------------- #
# -------------------------------------------------- PAGE -------------------------------------------------- #
# -------------------------------------------------- PAGE -------------------------------------------------- #
# -------------------------------------------------- PAGE -------------------------------------------------- #
# -------------------------------------------------- PAGE -------------------------------------------------- #


@app.route('/')
def home_page():
    permission.check_user_permission(session)

    # db_session = derive_db_session()
    # user_id = session['user']['id']
    # roles = db_session.query(model.Permission)\
    #     .outerjoin(model.UserRole, model.User.id==model.UserRole.user_id)\
    #     .outerjoin(model.Role, model.Role.id==model.UserRole.role_id).filter_by(id=user_id).all()
    # roles = db_session.execute(
    #     'select username,role.name,role.label,role.description from (user left join user_role on user.id = user_role.user_id) left join role on user_role.role_id = role.id;')
    # for r in roles:
    #     print(r)

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

    return jsonify(json.loads(response))


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

    user.last_login_at = time.time()

    try:
        db_session.commit()
        session['user'] = model.to_dict(user)
    except sqlalchemy.exc.DataError as e:
        db_session.rollback()
        return abort(make_response(str(e), 500))
    finally:
        db_session.close()

    return jsonify({'message': '登录成功'})


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

    user = db_session.query(model.User).filter_by(username=username).first()

    user_role = model.UserRole(user.id, model.Role.USER)
    try:
        db_session.add(user_role)
        db_session.commit()
    except sqlalchemy.exc.DataError as e:
        db_session.rollback()
        return abort(make_response(str(e), 500))

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

    return jsonify({'message': '注册成功'})


@app.route('/api/invitation', methods=['GET', 'POST', 'DELETE'])
def api_invitation_code():
    if request.method == 'GET':
        return api_get_invitation_code()
    elif request.method == 'POST':
        return api_create_invitation_code()
    elif request.method == 'DELETE':
        return api_delete_invitation_code()


def api_get_invitation_code():
    pass


def api_create_invitation_code():
    pass


def api_delete_invitation_code():
    pass


if __name__ == '__main__':
    create_app()
    # create_app('configs.ProductionConfig')
    host = app.config['HOST']
    port = app.config['PORT']
    app.run(host=host, port=port)
