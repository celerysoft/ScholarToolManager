#!/usr/bin/python3
# -*-coding:utf-8 -*-
import datetime
import ssl

import hashlib
import urllib

import math

import markdown2
import random
import re

import os
import sqlalchemy
from flask import make_response, jsonify, json, request, session, abort, g
from flask.views import MethodView

import configs
import database
import exception
import model
import permission
from util import date_util, shadowsocks_controller

app = None


def init_app(app_instance):
    global app
    app = app_instance


_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

__SHA1_PASSWORD_SALT = None


def derive_sha1_password_salt():
    global __SHA1_PASSWORD_SALT
    if __SHA1_PASSWORD_SALT is None:
        __SHA1_PASSWORD_SALT = app.config['SHA1_SALT']
    return __SHA1_PASSWORD_SALT


__ITEM_PER_PAGE = None


def get_item_per_page():
    global __ITEM_PER_PAGE
    if __ITEM_PER_PAGE is None:
        __ITEM_PER_PAGE = app.config['ITEM_PER_PAGE']
    return __ITEM_PER_PAGE


__URL_OF_BLOG_IMAGE = None


def get_url_of_blog_image():
    global __URL_OF_BLOG_IMAGE
    if __URL_OF_BLOG_IMAGE is None:
        __URL_OF_BLOG_IMAGE = app.config['URL_OF_BLOG_IMAGE']
    return __URL_OF_BLOG_IMAGE


__SERVICE_MIN_PORT = None


def get_service_min_port():
    global __SERVICE_MIN_PORT
    if __SERVICE_MIN_PORT is None:
        __SERVICE_MIN_PORT = app.config['SERVICE_MIN_PORT']
    return __SERVICE_MIN_PORT


def log_exception(exception):
    logger = derive_app_logger()
    if logger is not None:
        logger.exception(exception)


def derive_app_logger():
    app_logger = getattr(g, '_app_logger', None)
    if app_logger is None:
        app_logger = g._app_logger = app.logger
    return app_logger


def derive_db_session():
    return database.derive_db_session()


def derive_user_id_from_session():
    if 'user' in session.keys():
        return session['user']['id']
    else:
        return None


def derive_page_parameter(query):
    page = request.args.get('page')
    try:
        page = int(page) if page is not None else 1
    except ValueError:
        # noinspection PyUnresolvedReferences
        raise exception.api.InvalidRequest('Invalid page field.')
    page_size = request.args.get('page_size')
    try:
        page_size = int(page_size) if page_size is not None else __ITEM_PER_PAGE
    except ValueError:
        page_size = __ITEM_PER_PAGE
    offset = (page - 1) * page_size

    record_count = query.count()

    if 0 < record_count <= offset:
        # noinspection PyUnresolvedReferences
        raise exception.api.InvalidRequest('Item index is out of bounds, try modify page and page_size.')
    max_page = math.ceil(record_count / page_size)

    return page, page_size, offset, max_page


# -------------------------------------------------- decorators -------------------------------------------------- #
# -------------------------------------------------- decorators -------------------------------------------------- #
# -------------------------------------------------- decorators -------------------------------------------------- #
# -------------------------------------------------- decorators -------------------------------------------------- #
# -------------------------------------------------- decorators -------------------------------------------------- #
def login_required(f):
    def decorator(*args, **kwargs):
        permission.check_user_api_permission()
        return f(*args, **kwargs)

    return decorator


class DocumentMethodView(MethodView):
    def __init__(self):
        self._API_DOCUMENTATION_URL = 'coming soon...'

    def api_document(self, message='', code=400):
        msg = jsonify({
            'message': message,
            'documentation_url': self._API_DOCUMENTATION_URL
        })
        return make_response(msg, code)


class BaseView(DocumentMethodView):
    pass


class UserView(DocumentMethodView):
    decorators = [login_required]


class TestApi(MethodView):
    methods = ['GET', 'POST', 'DELETE']

    def get(self):
        return make_response('ok', 200)

    def post(self):
        debug = app.config['DEBUG']
        if not debug:
            return make_response('Method Not Allowed', 405)

        port = request.json['port']
        password = request.json['password']
        shadowsocks_controller.add_port(port, password)

        return make_response('指令已发送', 200)

    def delete(self):
        debug = app.config['DEBUG']
        if not debug:
            return make_response('Method Not Allowed', 405)

        port = request.json['port']
        shadowsocks_controller.remove_port(port)

        return make_response('指令已发送', 200)


class TodayInHistoryAPI(MethodView):
    methods = ['GET']

    def get(self):
        api_url = 'http://www.ipip5.com/today/api.php?type=json'

        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # noinspection PyUnresolvedReferences
        http_request = urllib.request.Request(api_url)
        # noinspection PyUnresolvedReferences
        response = urllib.request.urlopen(http_request, context=context).read()

        return make_response(jsonify(json.loads(response)), 200)


class ReCaptchaApi(MethodView):
    methods = ['POST']

    def post(self):
        api_url = 'https://www.recaptcha.net/recaptcha/api/siteverify'

        g_response = request.json['response']

        secret_key = None
        debug = app.config['DEBUG']
        if debug:
            secret_key = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'
        else:
            secret_key = app.config['RE_CAPTCHA_SECRET_KEY']
        data = {
            'secret': secret_key,
            'response': g_response,
        }
        data = urllib.parse.urlencode(data).encode()
        # noinspection PyUnresolvedReferences
        http_request = urllib.request.Request(api_url, method='POST', data=data)
        response = None
        # 6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe
        try:
            # noinspection PyUnresolvedReferences
            response = urllib.request.urlopen(http_request).read()
        except Exception as e:
            return make_response('人机身份验证过程发生未知错误，请重试', 500)

        response_dict = json.loads(response)
        if response_dict['success']:
            api_response = {
                'message': '人机身份验证成功'
            }
            return make_response(jsonify(api_response), 200)
        else:
            api_response = {
                'message': '你没有通过人机身份验证'
            }
            return make_response(jsonify(api_response), 400)


class LoginAPI(BaseView):
    methods = ['GET', 'POST']

    def get(self):
        return self.api_document()

    def post(self):
        name = request.json['name']
        password = request.json['password']
        db_session = derive_db_session()
        if name is not None:
            user = db_session.query(model.User).filter_by(username=name).first()
            if user is None:
                user = db_session.query(model.User).filter_by(email=name).first()
                if user is None:
                    return self.api_document('用户不存在', 400)

        else:
            return self.api_document('请输入用户名或邮箱', 400)

        # 检查密码
        sha1 = hashlib.sha1()
        sha1.update(derive_sha1_password_salt().encode('utf-8'))
        sha1.update(b':')
        sha1.update(password.encode('utf-8'))
        if user.password != sha1.hexdigest():
            return self.api_document('密码错误，请重试', 400)

        if not permission.check_login_permission(db_session, user.id):
            user_role = db_session.query(model.UserRole).filter(model.UserRole.user_id == user.id).first()
            if user_role is None:
                user_role = model.UserRole(user.id, model.Role.USER)
                try:
                    db_session.add(user_role)
                    db_session.commit()
                except sqlalchemy.exc.DataError as e:
                    db_session.rollback()
                    return self.api_document('服务器内部错误，请稍后再试', 500)
            else:
                return self.api_document('该用户已被关进小黑屋，请联系管理员进行申诉', 403)

        user.last_login_at = datetime.datetime.now().timestamp()

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
            'documentation_url': self._API_DOCUMENTATION_URL
        }), 200)


class RegisterAPI(BaseView):
    methods = ['GET', 'POST']

    def get(self):
        return self.api_document()

    def post(self):
        username = request.json['name']
        email = request.json['email']
        password = request.json['password']
        code = request.json['invitation_code']

        global _RE_EMAIL
        global _RE_SHA1
        if not username or not username.strip():
            return self.api_document('请输入用户名', 400)
        if not email or not _RE_EMAIL.match(email):
            return self.api_document('请输入正确的邮箱', 400)
        if not password or not _RE_SHA1.match(password):
            return self.api_document('请输入符合规则的密码', 400)

        db_session = derive_db_session()
        users = db_session.query(model.User).filter_by(username=username).all()
        if users is not None and len(users) > 0:
            return self.api_document('用户名已经存在', 400)
        users = db_session.query(model.User).filter_by(email=email).all()
        if users is not None and len(users) > 0:
            return self.api_document('邮箱已被注册', 400)

        invitation_code = db_session.query(model.InvitationCode).filter_by(code=code).first()
        if invitation_code is None:
            return self.api_document('邀请码不存在', 400)
        elif not invitation_code.available:
            return self.api_document('邀请码已被使用', 400)

        # 将记录写入user表
        sha1_password = '%s:%s' % (derive_sha1_password_salt(), password)
        user = model.User(username=username.strip(), email=email, name=username.strip(),
                          password=hashlib.sha1(sha1_password.encode('utf-8')).hexdigest(),
                          image='https://api.adorable.io/avatars/285/%s.png' % hashlib.md5(
                              email.encode('utf-8')).hexdigest())

        try:
            db_session.add(user)
            db_session.commit()
            session['user'] = model.to_dict(user)
        except BaseException as e:
            log_exception(e)
            return self.api_document('服务器内部错误，请刷新重试', 500)
        except sqlalchemy.exc.DataError as e:
            db_session.rollback()
            return abort(make_response(str(e), 500))

        # user = db_session.query(model.User).filter_by(username=username).first()

        # 将记录写入user_role表
        user_role = model.UserRole(user.id, model.Role.USER)
        db_session.add(user_role)

        # 将记录写入invitation_code表
        invitation_code.available = False
        invitation_code.invitee_id = user.id
        invitation_code.invited_at = datetime.datetime.now().timestamp()

        # 将记录写入user_scholar_balance表
        __SCHOLAR_BALANCE_FOR_NEW_USER = configs.Config.NEW_USER_SCHOLAR_BALANCE
        user_scholar_balance = model.UserScholarBalance(user.id, __SCHOLAR_BALANCE_FOR_NEW_USER)
        db_session.add(user_scholar_balance)

        try:
            db_session.commit()
        except BaseException as e:
            log_exception(e)
            return self.api_document('服务器内部错误，请刷新重试', 500)
        except sqlalchemy.exc.DataError as e:
            db_session.rollback()
            return abort(make_response(str(e), 500))
        finally:
            db_session.close()

        return make_response(jsonify({
            'message': '注册成功',
            'documentation_url': self._API_DOCUMENTATION_URL
        }), 200)


class UserAPI(UserView):
    methods = ['GET', 'POST', 'PATCH']

    def get(self):
        return self.api_document()

    def post(self):
        return self.api_document()

    def patch(self):
        # TODO OAUTH
        current_user_id = derive_user_id_from_session()

        db_session = derive_db_session()
        permission.check_manage_role_permission(db_session, current_user_id)

        user_id = request.json['user_id']
        if user_id is None:
            return self.api_document('Need user_id field')
        role_id = request.json['role_id']
        if role_id is None:
            return self.api_document('Need role_id field')

        user_role = db_session.query(model.UserRole) \
            .filter(model.User.id == model.UserRole.user_id) \
            .filter(model.UserRole.role_id == model.Role.id) \
            .filter(model.User.id == user_id).first()

        user_role.role_id = role_id

        try:
            db_session.commit()
        except BaseException as e:
            log_exception(e)
            return self.api_document('服务器内部错误，请刷新重试', 500)
        except sqlalchemy.exc.DataError as e:
            db_session.rollback()
            return abort(make_response(str(e), 500))
        finally:
            db_session.close()

        return make_response(jsonify({
            'message': '修改用户角色成功',
            'documentation_url': self._API_DOCUMENTATION_URL
        }), 201)


class InvitationCodeAPI(UserAPI):
    methods = ['GET', 'POST', 'DELETE']

    @classmethod
    def derive_invitation_code(cls):
        seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+=-"
        codes = []
        for i in range(32):
            codes.append(random.choice(seed))
        invitation_code = ''.join(codes)
        return invitation_code

    def get(self):
        return self.api_document()

    def post(self):
        # TODO OAUTH
        user_id = derive_user_id_from_session()
        db_session = derive_db_session()
        if user_id is None:
            return self.api_document('Need user_id')
        if not permission.check_manage_invitation_code_permission(db_session, user_id, True):
            raise exception.api.Forbidden('ID为%s的用户无权创建邀请码' % user_id)

        invitation_code = None
        invitation = 1
        while invitation is not None:
            invitation_code = InvitationCodeAPI.derive_invitation_code()
            invitation = db_session.query(model.InvitationCode) \
                .filter(model.InvitationCode.code == invitation_code).first()

        invitation = model.InvitationCode(invitation_code, user_id)

        try:
            db_session.add(invitation)
            db_session.commit()
        except BaseException as e:
            log_exception(e)
            return self.api_document('服务器内部错误，请刷新重试', 500)
        except sqlalchemy.exc.DataError as e:
            db_session.rollback()
            return abort(make_response(str(e), 500))
        finally:
            db_session.close()

        return make_response(jsonify({
            'message': '生成邀请码成功',
            'code': invitation_code,
            'documentation_url': self._API_DOCUMENTATION_URL
        }), 201)

    def delete(self):
        return self.api_document()


class PermissionAPI(UserAPI):
    methods = ['GET']

    def get(self):
        # TODO OAUTH
        db_session = derive_db_session()
        user_id = derive_user_id_from_session()

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
                return self.api_document('ID为%s的用户无权进行用户管理' % user_id)

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
                return self.api_document('ID为%s的用户无权进行角色管理' % user_id)

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


class EventAPI(UserView):
    methods = ['GET', 'POST', 'PATCH', 'DELETE']

    def get(self):
        event_id = request.args.get('id')
        if event_id is None:
            return self.api_document()

        db_session = derive_db_session()
        event = db_session.query(model.Event).filter_by(id=event_id).first()
        if event is None:
            return self.api_document('id为%s的公告不存在' % event_id, 404)

        data = model.to_dict(event)

        html_version = request.args.get('html')
        if html_version:
            html_content = markdown2.markdown(event.content, extras=['fenced-code-blocks', 'tables', 'toc'])
            html_content = html_content.replace('{{ image }}', get_url_of_blog_image())
            data['html'] = html_content

        return make_response(
            jsonify({
                'message': '获取公告成功',
                'event': data,
                'documentation_url': self._API_DOCUMENTATION_URL
            }), 200
        )

    def post(self):
        # TODO OAUTH
        user_id = derive_user_id_from_session()
        db_session = derive_db_session()
        if user_id is None:
            return self.api_document('Need user_id')
        if not permission.check_manage_event_permission(db_session, user_id):
            raise exception.api.Forbidden('ID为%s的用户无权创建公告' % user_id)

        name = request.json['name']
        tag = request.json['tag']
        summary = request.json['summary']
        content = request.json['content']

        if not name or not name.strip():
            return self.api_document('公告名字不能为空', 400)
        if not summary or not summary.strip():
            return self.api_document('公告描述不能为空', 400)
        if not content or not content.strip():
            return self.api_document('公告内容不能为空', 400)

        event = model.Event(user_id=user_id, name=name.strip(), tag=tag, summary=summary.strip(),
                            content=content.strip())
        try:
            db_session.add(event)
            db_session.commit()
        except BaseException as e:
            log_exception(e)
            return self.api_document('服务器内部错误，请刷新重试', 500)
        except sqlalchemy.exc.DataError as e:
            db_session.rollback()
            return abort(make_response(str(e), 500))
        finally:
            db_session.close()

        return make_response(
            jsonify({
                'message': '发布公告成功',
                'documentation_url': self._API_DOCUMENTATION_URL
            }), 201
        )

    def patch(self):
        # TODO OAUTH
        user_id = derive_user_id_from_session()
        db_session = derive_db_session()
        if user_id is None:
            return self.api_document('Need user_id')
        if not permission.check_manage_event_permission(db_session, user_id):
            raise exception.api.Forbidden('ID为%s的用户无权编辑公告' % user_id)

        id = request.json['id']
        name = request.json['name']
        tag = request.json['tag']
        summary = request.json['summary']
        content = request.json['content']

        if not name or not name.strip():
            return self.api_document('公告名字不能为空', 400)
        if not summary or not summary.strip():
            return self.api_document('公告描述不能为空', 400)
        if not content or not content.strip():
            return self.api_document('公告内容不能为空', 400)

        db_session.query(model.Event).filter_by(id=id).update({
            'name': name,
            'tag': tag,
            'summary': summary,
            'content': content
        })

        try:
            db_session.commit()
        except BaseException as e:
            log_exception(e)
            return self.api_document('服务器内部错误，请刷新重试', 500)
        except sqlalchemy.exc.DataError as e:
            db_session.rollback()
            return abort(make_response(str(e), 500))
        finally:
            db_session.close()

        return make_response(
            jsonify({
                'message': '修改公告成功',
                'documentation_url': self._API_DOCUMENTATION_URL
            }), 201
        )

    def delete(self):
        # TODO OAUTH
        user_id = derive_user_id_from_session()
        db_session = derive_db_session()
        if not permission.check_manage_event_permission(db_session, user_id):
            raise exception.api.Forbidden('ID为%s的用户无权删除公告' % user_id)

        product_id = request.json['id']
        if not product_id:
            return self.api_document('所需删除的公告id不能为空', 400)

        product = db_session.query(model.Event).filter_by(id=product_id).first()
        if not product:
            return self.api_document('id为%s公告不存在，故无法删除' % product_id, 404)

        try:
            db_session.delete(product)
            db_session.commit()
        except BaseException as e:
            log_exception(e)
            return self.api_document('服务器内部错误，请刷新重试', 500)
        except sqlalchemy.exc.DataError as e:
            db_session.rollback()
            return abort(make_response(str(e), 500))
        finally:
            db_session.close()

        return make_response(
            jsonify({
                'message': '删除公告成功',
                'documentation_url': self._API_DOCUMENTATION_URL
            }), 204
        )


class RoleAPI(UserView):
    methods = ['GET', 'POST', 'PATCH', 'DELETE']

    def get(self):
        # TODO OAUTH
        current_user_id = derive_user_id_from_session()

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
            'documentation_url': self._API_DOCUMENTATION_URL,
            'roles': role_list
        }
        if user_role is not None:
            result['user_role'] = model.to_dict(user_role)

        return make_response(jsonify(result), 200)

    def post(self):
        # TODO OAUTH
        current_user_id = derive_user_id_from_session()

        db_session = derive_db_session()
        permission.check_manage_role_permission(db_session, current_user_id)

        name = request.json['name']
        if name is None:
            return self.api_document('Need name field')
        label = request.json['label']
        if label is None:
            return self.api_document('Need label field')
        description = request.json['description']
        # if description is None:
        #     return self.api_document('Need description field')
        permissions = request.json['permissions']
        # if permissions is None:
        #     return self.api_document('Need permissions field')

        role = model.Role(name, label, description)
        try:
            db_session.add(role)
            db_session.commit()
        except BaseException as e:
            log_exception(e)
            return self.api_document('服务器内部错误，请刷新重试', 500)
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
        except BaseException as e:
            log_exception(e)
            return self.api_document('服务器内部错误，请刷新重试', 500)
        except sqlalchemy.exc.DataError as e:
            db_session.rollback()
            return abort(make_response(str(e), 500))
        finally:
            db_session.close()

        return make_response(
            jsonify({
                'message': '创建角色成功',
                'role_id': role_id,
                'documentation_url': self._API_DOCUMENTATION_URL
            }), 201
        )

    def patch(self):
        # TODO OAUTH
        user_id = derive_user_id_from_session()

        db_session = derive_db_session()
        permission.check_manage_role_permission(db_session, user_id)

        role_id = request.json['id']
        if role_id is None:
            return self.api_document('Need id field')
        name = request.json['name']
        if name is None:
            return self.api_document('Need name field')
        label = request.json['label']
        if label is None:
            return self.api_document('Need label field')
        description = request.json['description']
        # if description is None:
        #     return self.api_document('Need description field')
        permissions = request.json['permissions']
        # if permissions is None:
        #     return self.api_document('Need permissions field')

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
        except BaseException as e:
            log_exception(e)
            return self.api_document('服务器内部错误，请刷新重试', 500)
        except sqlalchemy.exc.DataError as e:
            db_session.rollback()
            return abort(make_response(str(e), 500))
        finally:
            db_session.close()

        return make_response(
            jsonify({
                'message': '更新角色成功',
                'role_id': role_id,
                'documentation_url': self._API_DOCUMENTATION_URL
            }), 201
        )

    def delete(self):
        # TODO OAUTH
        user_id = derive_user_id_from_session()
        db_session = derive_db_session()
        if not permission.check_manage_event_permission(db_session, user_id):
            raise exception.api.Forbidden('ID为%s的用户无权删除角色' % user_id)

        role_id = request.json['id']
        if not role_id:
            return self.api_document('所需删除的角色id不能为空', 400)

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
            return self.api_document('id为%s公告不存在，故无法删除' % role_id, 404)

        try:
            db_session.delete(role)
            db_session.commit()
        except BaseException as e:
            log_exception(e)
            return self.api_document('服务器内部错误，请刷新重试', 500)
        except sqlalchemy.exc.DataError as e:
            db_session.rollback()
            return abort(make_response(str(e), 500))
        finally:
            db_session.close()

        return make_response(
            jsonify({
                'message': '删除角色成功',
                'documentation_url': self._API_DOCUMENTATION_URL
            }), 204
        )


class ServiceTemplateAPI(UserView):
    methods = ['GET', 'POST', 'PATCH', 'DELETE']

    def get(self):
        service_template_id = request.args.get('id')
        if service_template_id is None:
            return self.api_document('Need id field.')

        db_session = derive_db_session()

        service_template = db_session.query(model.ServiceTemplate) \
            .filter(model.ServiceTemplate.id == service_template_id).first()

        if service_template is None:
            return self.api_document('ID为%s的套餐模板不存在' % service_template_id, 404)

        return make_response(
            jsonify({
                'message': '获取套餐模板成功',
                'template': model.to_dict(service_template),
                'documentation_url': self._API_DOCUMENTATION_URL
            }), 200
        )

    def post(self):
        # TODO OAUTH2
        user_id = derive_user_id_from_session()
        db_session = derive_db_session()
        if not permission.check_manage_service_template_permission(db_session, user_id):
            raise exception.api.Forbidden('ID为%s的用户无权创建套餐模版' % user_id)

        service_type = request.json['type']
        if service_type is None:
            return self.api_document('Need type field.')
        title = request.json['title']
        if title is None:
            return self.api_document('Need title field.')
        subtitle = request.json['subtitle']
        if subtitle is None:
            return self.api_document('Need subtitle field.')
        description = request.json['description']
        if description is None:
            return self.api_document('Need description field.')
        balance = request.json['balance']
        if balance is None:
            return self.api_document('Need balance field.')
        price = request.json['price']
        if price is None:
            return self.api_document('Need price field.')
        initialization_fee = request.json['initialization_fee']
        if initialization_fee is None:
            return self.api_document('Need initialization_fee field.')

        service_template = model.ServiceTemplate(service_type, title, subtitle, description, balance, price,
                                                 initialization_fee)
        db_session.add(service_template)

        try:
            db_session.commit()
        except BaseException as e:
            log_exception(e)
            return self.api_document('服务器内部错误，请刷新重试', 500)
        except sqlalchemy.exc.DataError as e:
            db_session.rollback()
            return abort(make_response(str(e), 500))
        finally:
            db_session.close()

        return make_response(
            jsonify({
                'message': '创建套餐模板成功',
                'documentation_url': self._API_DOCUMENTATION_URL
            }), 201
        )

    def patch(self):
        """
        api_update_service_template
        :return:
        """
        # TODO OAUTH2
        user_id = derive_user_id_from_session()
        db_session = derive_db_session()
        if not permission.check_manage_service_template_permission(db_session, user_id):
            raise exception.api.Forbidden('ID为%s的用户无权修改套餐模版' % user_id)

        service_id = request.json.get('id', None)
        if service_id is None:
            return self.api_document('Need id field.')
        service_type = request.json.get('type', None)
        if service_type is None:
            return self.api_document('Need type field.')
        title = request.json.get('title', None)
        if title is None:
            return self.api_document('Need title field.')
        subtitle = request.json.get('subtitle', None)
        if subtitle is None:
            return self.api_document('Need subtitle field.')
        description = request.json.get('description', None)
        if description is None:
            return self.api_document('Need description field.')
        balance = request.json.get('balance', None)
        if balance is None:
            return self.api_document('Need balance field.')
        price = request.json.get('price', None)
        if price is None:
            return self.api_document('Need price field.')
        initialization_fee = request.json.get('initialization_fee', None)
        if initialization_fee is None:
            return self.api_document('Need initialization_fee field.')
        available = request.json.get('available', None)
        if available is None:
            return self.api_document('Need available field.')

        service_template = db_session.query(model.ServiceTemplate).filter(
            model.ServiceTemplate.id == service_id).first()

        if service_template is None:
            return self.api_document('ID为%s的套餐模板不存在' % service_id, 404)

        service_template.type = service_type
        service_template.title = title
        service_template.subtitle = subtitle
        service_template.description = description
        service_template.balance = balance
        service_template.price = price
        service_template.initialization_fee = initialization_fee
        service_template.available = available

        try:
            db_session.commit()
        except BaseException as e:
            log_exception(e)
            return self.api_document('服务器内部错误，请刷新重试', 500)
        except sqlalchemy.exc.DataError as e:
            db_session.rollback()
            return abort(make_response(str(e), 500))
        finally:
            db_session.close()

        return make_response(
            jsonify({
                'message': '编辑套餐模板成功',
                'documentation_url': self._API_DOCUMENTATION_URL
            }), 201
        )

    def delete(self):
        """
        api_delete_service_template
        :return:
        """
        # TODO OAUTH2
        user_id = derive_user_id_from_session()
        db_session = derive_db_session()
        if not permission.check_manage_service_template_permission(db_session, user_id):
            raise exception.api.Forbidden('ID为%s的用户无权删除套餐模版' % user_id)

        service_template_id = request.json['id']
        if service_template_id is None:
            return self.api_document('Need id field.')

        service_template = db_session.query(model.ServiceTemplate).filter(
            model.ServiceTemplate.id == service_template_id).first()
        db_session.delete(service_template)

        try:
            db_session.commit()
        except BaseException as e:
            log_exception(e)
            return self.api_document('服务器内部错误，请刷新重试', 500)
        except sqlalchemy.exc.DataError as e:
            db_session.rollback()
            return abort(make_response(str(e), 500))
        finally:
            db_session.close()

        return make_response(
            jsonify({
                'message': '删除套餐模板成功',
                'documentation_url': self._API_DOCUMENTATION_URL
            }), 204
        )


class ServiceAPI(UserView):
    methods = ['GET', 'POST', 'PATCH']

    def get(self):
        # TODO OAUTH2
        permission.check_user_api_permission()

        query_user_id = request.args.get('user_id')
        query_service_id = request.args.get('id')
        if query_user_id is not None:
            return self.api_get_user_service(query_user_id)
        if query_service_id is not None:
            return self.api_get_service_by_id(query_service_id)
        else:
            return self.api_get_service_on_sale()

    def api_get_user_service(self, query_user_id):
        # 分页示例

        db_session = derive_db_session()

        query = db_session.query(model.Service) \
            .filter(model.UserService.user_id == query_user_id) \
            .filter(model.UserService.service_id == model.Service.id)

        page, page_size, offset, max_page = derive_page_parameter(query)

        services = query.offset(offset).limit(page_size).all()

        service_list = []

        for s in services:
            service = model.to_dict(s)
            template = db_session.query(model.ServiceTemplate).filter(model.ServiceTemplate.id == s.template_id).first()
            service_password = db_session.query(model.ServicePassword) \
                .filter(model.ServicePassword.service_id == s.id).first()
            service['title'] = template.title
            service['price'] = template.price
            service['port'] = service_password.port
            service_list.append(service)

        return make_response(
            jsonify({
                'message': '获取用户套餐信息成功',
                'page': page,
                'page_size': page_size,
                'max_page': max_page,
                'service': service_list,
                'documentation_url': self._API_DOCUMENTATION_URL
            }), 200
        )

    def api_get_service_by_id(self, service_id):
        db_session = derive_db_session()

        query = db_session.query(model.Service).filter(model.Service.id == service_id)
        service = query.first()

        if service is None:
            return self.api_document('指定id的套餐不存在', 404)

        template = db_session.query(model.ServiceTemplate).filter(
            model.ServiceTemplate.id == service.template_id).first()
        service_password = db_session.query(model.ServicePassword) \
            .filter(model.ServicePassword.service_id == service.id).first()
        service_dict = model.to_dict(service)
        service_dict['type'] = template.type
        service_dict['title'] = template.title
        service_dict['price'] = template.price
        service_dict['port'] = service_password.port
        service_dict['password'] = service_password.password
        if template.type == model.ServiceTemplate.MONTHLY:
            service_dict['renew_at'] = service.reset_at
        else:
            service_dict['renew_at'] = service.expired_at

        return make_response(
            jsonify({
                'message': '获取套餐详情成功',
                'service': service_dict,
                'documentation_url': self._API_DOCUMENTATION_URL
            }), 200
        )

    def api_get_service_on_sale(self):
        return self.api_document()

    def post(self):
        """
        api_create_service
        :return:
        """
        user_id = derive_user_id_from_session()
        db_session = derive_db_session()
        if not permission.check_manage_service_permission(db_session, user_id, True):
            raise exception.api.Forbidden("无权创建套餐")

        service_template_id = None
        try:
            service_template_id = request.json['template_id']
        except KeyError:
            return self.api_document('Need template_id field.')
        try:
            password = request.json['password']
        except KeyError:
            return self.api_document('Need password field.')
        service_template = db_session.query(model.ServiceTemplate) \
            .filter(model.ServiceTemplate.id == service_template_id).first()
        if not service_template.available:
            return self.api_document('该套餐已下架，故无法办理', 403)

        # 扣费
        total_payment = service_template.initialization_fee + service_template.price
        user_scholar_balance = db_session.query(model.UserScholarBalance) \
            .filter(model.UserScholarBalance.user_id == user_id).first()
        balance = user_scholar_balance.balance
        if balance < total_payment:
            return self.api_document('余额不足', 403)
        else:
            user_scholar_balance.balance -= total_payment

        # 创建服务
        service_type = service_template.type
        now = datetime.datetime.now()
        created_at = now
        last_reset_at = None
        auto_renew = None
        if service_type == model.ServiceTemplate.MONTHLY:
            try:
                auto_renew = request.json['auto_renew']
            except KeyError:
                return self.api_document('Need auto_renew field.')
            reset_at = date_util.derive_1st_of_next_month(now)
            if auto_renew:
                expired_at = datetime.datetime(2099, 12, 31, 23, 59, 59).timestamp()
            else:
                expired_at = reset_at
        elif service_type == model.ServiceTemplate.DATA:
            reset_at = None
            expired_at = datetime.datetime.fromtimestamp(created_at.timestamp() + 365 * 24 * 60 * 60)
        else:
            return self.api_document('Unknow template type.')

        service = model.Service(
            template_id=service_template_id,
            type=service_type,
            usage=0,
            package=service_template.balance,
            reset_at=reset_at,
            last_reset_at=last_reset_at,
            created_at=created_at,
            expired_at=expired_at,
            total_usage=0,
            auto_renew=auto_renew
        )
        db_session.add(service)

        try:
            db_session.commit()
        except BaseException as e:
            log_exception(e)
            return self.api_document('服务器内部错误，请刷新重试', 500)
        except sqlalchemy.exc.DataError as e:
            db_session.rollback()
            return abort(make_response(str(e), 500))

        service_id = service.id

        # 关联user_service表
        user_service = model.UserService(user_id, service_id)
        db_session.add(user_service)

        # 关联service_password表
        service_port = self.derive_available_shadowsocks_port(db_session)

        service_password = model.ServicePassword(service.id, service_port, password)
        db_session.add(service_password)

        try:
            db_session.commit()
        except BaseException as e:
            log_exception(e)
            return self.api_document('服务器内部错误，请刷新重试', 500)
        except sqlalchemy.exc.DataError as e:
            db_session.rollback()
            return abort(make_response(str(e), 500))
        finally:
            db_session.close()

        shadowsocks_controller.add_port(service_port, password)

        return make_response(
            jsonify({
                'message': '创建套餐成功',
                'service_id': service_id,
                'documentation_url': self._API_DOCUMENTATION_URL
            }), 201
        )

    def derive_available_shadowsocks_port(self, db_session):
        service_password = db_session.query(model.ServicePassword) \
            .order_by(model.ServicePassword.port.desc()) \
            .filter(model.Service.alive.is_(True)) \
            .filter(model.Service.id == model.ServicePassword.service_id).first()

        if service_password is None:
            return get_service_min_port()
        else:
            return service_password.port + 1

    def patch(self):
        """
        api_update_service
        :return:
        """
        user_id = derive_user_id_from_session()
        db_session = derive_db_session()
        # if not permission.check_manage_service_permission(db_session, user_id, True):
        #     raise exception.api.Forbidden("无权创建套餐")

        # 获取key示例
        service_id = None
        try:
            service_id = request.json['id']
        except KeyError:
            return self.api_document('Need service_id field.')
        auto_renew = None
        try:
            auto_renew = request.json['auto_renew']
        except KeyError:
            pass
        renew = None
        try:
            renew = request.json['renew']
        except KeyError:
            pass

        user_service = db_session.query(model.UserService) \
            .filter(model.UserService.user_id == user_id) \
            .filter(model.UserService.service_id == service_id).first()
        if user_service is None:
            raise exception.api.Forbidden("无权修改套餐")

        service = db_session.query(model.Service) \
            .filter(model.Service.id == service_id).first()

        service_template_id = service.template_id
        service_template = db_session.query(model.ServiceTemplate) \
            .filter(model.ServiceTemplate.id == service_template_id).first()

        # 修改自动续费
        now = datetime.datetime.now()
        if auto_renew is not None and service_template.type == model.ServiceTemplate.MONTHLY:
            service.auto_renew = auto_renew
            service.reset_at = date_util.derive_1st_datetime_of_next_month(now)
            if auto_renew:
                service.expired_at = datetime.datetime(2099, 12, 31, 23, 59, 59)
            else:
                service.expired_at = service.reset_at

        # 续费
        if renew is not None and renew is True:
            if not service_template.available:
                return self.api_document('该套餐已下架，无法办理续费', 403)

            # 判断是否还可以续费
            if not service.alive:
                return self.api_document('由于长期没有续费，该套餐已经被系统释放，无法进行续费操作，如有需要请新开学术套餐')

            # 判断是否在可续费时间内
            if service_template.type == model.ServiceTemplate.MONTHLY:
                if service.reset_at.timestamp() < now.timestamp() < (service.reset_at.timestamp() + 24 * 60 * 60):
                    pass
                else:
                    return self.api_document('当前不是有效的续费时间，请在每月1号进行续费')
            elif service_template.type == model.ServiceTemplate.DATA:
                if (service.package - service.usage <= service.package * 0.2
                    and now.timestamp() < service.expired_at.timestamp()) \
                        or (service.expired_at.timestamp() < now.timestamp() <
                            date_util.derive_1st_of_next_month(service.expired_at)):
                    pass
                else:
                    return self.api_document('当前不是有效的续费时间，或者剩余流量大于总流量的20%，无法续费')
            # 扣费
            total_payment = service_template.price
            user_scholar_balance = db_session.query(model.UserScholarBalance) \
                .filter(model.UserScholarBalance.user_id == user_id).first()
            balance = user_scholar_balance.balance
            if balance < total_payment:
                return self.api_document('余额不足', 403)
            else:
                user_scholar_balance.balance -= total_payment

            # 更新服务
            service.last_reset_at = now
            service.usage = 0
            if not service.available:
                service.available = True
                service_password = db_session.query(model.ServicePassword) \
                    .filter(model.ServicePassword.service_id == service_id).first()
                shadowsocks_controller.add_port(service_password.port, service_password.password)
            if service_template.type == model.ServiceTemplate.MONTHLY:
                auto_renew = request.json['auto_renew']
                if auto_renew is None:
                    return self.api_document('Need auto_renew field.')
                if auto_renew:
                    service.reset_at = date_util.derive_1st_datetime_of_next_month(now)
                    service.expired_at = datetime.datetime(2099, 12, 31, 23, 59, 59)
                else:
                    service.reset_at = None
                    service.expired_at = date_util.derive_1st_of_next_month(now)
            elif service_template.type == model.ServiceTemplate.DATA:
                service.expired_at = datetime.datetime.fromtimestamp(now.timestamp() + 365 * 24 * 60 * 60)

        try:
            db_session.commit()
        except BaseException as e:
            log_exception(e)
            return self.api_document('服务器内部错误，请刷新重试', 500)
        except sqlalchemy.exc.DataError as e:
            db_session.rollback()
            return abort(make_response(str(e), 500))
        finally:
            db_session.close()

        return make_response(
            jsonify({
                'message': '修改套餐成功',
                'documentation_url': self._API_DOCUMENTATION_URL
            }), 201
        )


class UsageAPI(BaseView):
    methods = ['GET', 'POST', 'PUT']

    def get(self):
        user_id = derive_user_id_from_session()
        db_session = derive_db_session()
        if not permission.check_manage_permission(db_session, user_id):
            raise exception.api.Forbidden("无权限")

        SHADOWSOCKS_LOG_FILE_PATH = app.config['SS_LISTENER_LOG_FILE']
        lines = []
        with open(SHADOWSOCKS_LOG_FILE_PATH, 'r') as f:
            lines = f.readlines()

        lines = lines[-10:] if len(lines) >= 10 else lines

        warning_message = None
        last_record = lines[-1] if len(lines) > 0 else None
        if last_record is not None:
            datetime_str = last_record.split(' - ')[0]
            last_record_datetime = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S,%f')
            if datetime.datetime.now().timestamp() - last_record_datetime.timestamp() > 12 * 60 * 60:
                warning_message = '最后一条记录产生于12小时之前，请检查是否需要重启监听服务'
            elif datetime.datetime.now().timestamp() - last_record_datetime.timestamp() < 0:
                warning_message = '最后一条记录产生在未来，我的天！请检查是否需要重启监听服务'
            else:
                warning_message = '监听服务运行正常'

        return make_response(
            jsonify({
                'usages': lines,
                'warning_message': warning_message,
                'message': '获取学术统计信息成功',
                'documentation_url': self._API_DOCUMENTATION_URL
            }), 200
        )

    def put(self):
        user_id = derive_user_id_from_session()
        db_session = derive_db_session()
        if not permission.check_manage_permission(db_session, user_id):
            raise exception.api.Forbidden("无权限")

        restart_shell_file = app.config['SS_LISTENER_RESTART_SHELL_FILE_PATH']
        status = os.system('. %s' % restart_shell_file)

        return make_response(
            jsonify({
                'message': '执行重启任务成功，返回信息：%s' % status,
                'documentation_url': self._API_DOCUMENTATION_URL
            }), 201
        )

    def post(self):
        # TODO 加强安全性

        data = request.data.decode('utf-8')
        data = data[6:]

        # print(data)

        db_session = derive_db_session()

        data = json.loads(data)
        for port, usage in data.items():
            # print('port %s use data: %s' % (port, usage))
            service = db_session.query(model.Service).filter(model.ServicePassword.port == port).filter(
                model.Service.id == model.ServicePassword.service_id).first()

            if service is None:
                continue

            if service.available:
                service.usage += usage
                service.total_usage += usage
                if service.usage > service.package:
                    service.available = False
                    shadowsocks_controller.remove_port(port)

        try:
            db_session.commit()
        except BaseException as e:
            log_exception(e)
            return abort(make_response(str(e), 500))
        except sqlalchemy.exc.DataError as e:
            db_session.rollback()
            return abort(make_response(str(e), 500))
        finally:
            db_session.close()

        return make_response(
            jsonify({
                'message': '学术统计信息接收成功',
                'documentation_url': self._API_DOCUMENTATION_URL
            }), 201
        )


class ScholarBalanceAPI(UserAPI):
    methods = ['GET', 'PATCH']

    def get(self):
        """
        api_get_scholar_balance
        :return:
        """
        query_user_id = request.args.get('user_id')
        if query_user_id is None:
            return self.api_document('Need user_id field.')

        db_session = derive_db_session()
        user_scholar_balance = db_session.query(model.UserScholarBalance) \
            .filter(model.UserScholarBalance.user_id == query_user_id).first()

        balance = user_scholar_balance.balance

        return make_response(
            jsonify({
                'message': '学术统计信息接收成功',
                'user_id': query_user_id,
                'balance': balance,
                'documentation_url': self._API_DOCUMENTATION_URL
            }), 200
        )

    def patch(self):
        """
        api_update_scholar_balance
        :return:
        """
        user_id = derive_user_id_from_session()
        db_session = derive_db_session()
        if not permission.check_manage_scholar_balance_permission(db_session, user_id, True):
            raise exception.api.Forbidden("无权管理学术积分")

        query_user_id = request.json['user_id']
        if query_user_id is None:
            return self.api_document('Need user_id field.')
        amount = int(request.json['amount'])
        if amount is None:
            return self.api_document('Need amount field.')

        user_scholar_balance = db_session.query(model.UserScholarBalance) \
            .filter(model.UserScholarBalance.user_id == query_user_id).first()

        user_scholar_balance.balance += amount

        user_scholar_balance_log = model.UserScholarBalanceLog(
            user_id=query_user_id,
            amount=amount,
            balance=user_scholar_balance.balance,
            message='系统发放'
        )
        db_session.add(user_scholar_balance_log)

        try:
            db_session.commit()
        except BaseException as e:
            log_exception(e)
            return self.api_document('服务器内部错误，请刷新重试', 500)
        except sqlalchemy.exc.DataError as e:
            db_session.rollback()
            return abort(make_response(str(e), 500))
        finally:
            db_session.close()

        return make_response(
            jsonify({
                'message': '充值学术积分成功',
                'documentation_url': self._API_DOCUMENTATION_URL
            }), 201
        )


class ServicePasswordAPI(UserAPI):
    methods = ['PATCH']

    def patch(self):
        """
        api_update_service_password
        :return:
        """
        user_id = derive_user_id_from_session()
        db_session = derive_db_session()

        service_id = None
        try:
            service_id = request.json['service_id']
        except KeyError:
            return self.api_document('Need service_id field.')
        new_password = None
        try:
            new_password = request.json['new_password']
        except KeyError:
            return self.api_document('Need new_password field.')
        if len(new_password) == 0:
            return self.api_document('密码长度至少为1，当前为0')

        service_password = db_session.query(model.ServicePassword) \
            .filter(model.ServicePassword.service_id == service_id) \
            .filter(model.UserService.service_id == model.ServicePassword.service_id) \
            .filter(model.UserService.user_id == user_id).first()
        if service_password is None:
            return self.api_document('套餐不存在或该套餐不属于当前用户', 404)

        service_password.password = new_password

        shadowsocks_controller.remove_port(service_password.port)
        shadowsocks_controller.add_port(service_password.port, service_password.password)

        try:
            db_session.commit()
        except BaseException as e:
            log_exception(e)
            return self.api_document('服务器内部错误，请刷新重试', 500)
        except sqlalchemy.exc.DataError as e:
            db_session.rollback()
            return abort(make_response(str(e), 500))
        finally:
            db_session.close()

        return make_response(
            jsonify({
                'message': '修改连接密码成功',
                'documentation_url': self._API_DOCUMENTATION_URL
            }), 201
        )
