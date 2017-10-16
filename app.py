import hashlib
import re
import time
import urllib

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


def derive_user_id_from_session():
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


@app.route('/manage/event/')
def manage_event():
    if not permission.check_manage_event_permission(derive_db_session(), derive_user_id_from_session()):
        return redirect(url_for('home_page'))

    page = request.args.get('page')
    try:
        page = int(page) if page is not None else 1
    except ValueError:
        return redirect(url_for('manage_event'))

    db_session = derive_db_session(pagination=True)
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
def create_product():
    if not permission.check_manage_event_permission(derive_db_session(), derive_user_id_from_session()):
        return redirect(url_for('home_page'))

    return render_template('manage_event_edit.html',
                           title='发布公告',
                           action='POST')


@app.route('/manage/event/edit/')
def edit_product():
    if not permission.check_manage_event_permission(derive_db_session(), derive_user_id_from_session()):
        return redirect(url_for('home_page'))

    product_id = request.args.get('id')
    return render_template('manage_event_edit.html',
                           title='编辑公告',
                           id=product_id,
                           action='PATCH')


@app.route('/manage/user/')
def manage_user():
    permission.check_user_permission()

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
    db_session = derive_db_session()
    user = db_session.query(model.User).filter_by(name=name).first()
    if user is None:
        return abort(404)

    return render_template('user.html',
                           title='用户' + name,
                           user=user)


@app.route('/event/')
def event():
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

    if not permission.check_login_permission(db_session, user.id):
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
    pass


def api_delete_invitation_code():
    pass


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
    user_id = request.args.get('user_id')
    if user_id is None:
        return permission_api_document()

    permission.check_user_api_permission()

    permissions = permission.derive_user_permissions(derive_db_session(), user_id)
    permission_list = []
    for p in permissions:
        permission_list.append(model.to_dict(p))
    return jsonify({
        'user_id': user_id,
        'permissions': permission_list
    })


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

    return jsonify(data)


def api_create_event():
    permission.check_user_api_permission()

    db_session = derive_db_session()
    if not permission.check_manage_event_permission(db_session, derive_user_id_from_session()):
        raise exception.api.Forbidden

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

    event = model.Event(user_id=session['user']['id'], name=name.strip(), tag=tag, summary=summary.strip(),
                        content=content.strip())
    try:
        db_session.add(event)
        db_session.commit()
    except sqlalchemy.exc.DataError as e:
        db_session.rollback()
        return abort(make_response(str(e), 500))
    finally:
        db_session.close()

    return jsonify({'message': '发布公告成功'})


def api_update_event():
    permission.check_user_api_permission()

    db_session = derive_db_session()
    if not permission.check_manage_event_permission(db_session, derive_user_id_from_session()):
        raise exception.api.Forbidden

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

    return jsonify({'message': '修改公告成功'})


def api_delete_event():
    """
    删除公告
    :return:
    """
    permission.check_user_api_permission()

    db_session = derive_db_session()
    if not permission.check_manage_event_permission(db_session, derive_user_id_from_session()):
        raise exception.api.Forbidden

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

    return jsonify({'message': '删除公告成功'})


if __name__ == '__main__':
    create_app()
    # create_app('configs.ProductionConfig')
    host = app.config['HOST']
    port = app.config['PORT']
    app.run(host=host, port=port)
