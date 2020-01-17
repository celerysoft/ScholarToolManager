# -*- coding: utf-8 -*-
import hashlib

import configs
from application import exception
from application.model.role import Role
from application.model.user import User
from application.model.user_role import UserRole
from application.util import authorization, permission
from application.util.database import session_scope
from application.views.base_api import BaseAPI, ApiResult


class LoginAPI(BaseAPI):
    methods = ['POST']

    def post(self):
        username = self.get_post_data('username', require=True, error_message='请输入用户名或邮箱')
        password = self.get_post_data('password', require=True, error_message='请输入密码')

        with session_scope() as session:
            user = session.query(User) \
                .filter(User.username == username, User.status != User.STATUS.DELETED).first()  # type:User
            if user is None:
                user = session.query(User).filter(User.email == username, User.status != User.STATUS.DELETED).first()
                if user is None:
                    raise exception.api.NotFound('用户不存在')

            hashed_password = authorization.toolkit.hash_plaintext(password)

            if user.password != hashed_password:
                sha1 = hashlib.sha1()
                sha1.update(configs.SHA1_SALT.encode('utf-8'))
                sha1.update(b':')
                sha1.update(password.encode('utf-8'))
                legacy_hash_password = sha1.hexdigest()
                if user.password != legacy_hash_password:
                    raise exception.api.InvalidRequest('密码错误，请重试')
                else:
                    user.password = hashed_password

            if user.status == User.STATUS.SUSPENDED:
                raise exception.api.Forbidden('用户已申请停用账号，如需恢复使用，请联系管理员')

            if not permission.toolkit.check_login_permission(session, user.uuid):
                user_role = session.query(UserRole).filter(UserRole.user_uuid == user.uuid).first()
                if user_role is None:
                    role = session.query(Role).fitler(
                        Role.name == Role.BuiltInRole.REGISTRATION_USER.value.name).first()  # type: Role
                    user_role = UserRole(user.uuid, role.uuid)
                    session.add(user_role)
                else:
                    raise exception.api.Forbidden('该用户已被拉黑，请联系管理员进行申诉')

            result = ApiResult('登录成功', payload={
                'jwt': authorization.toolkit.derive_jwt_token(user.uuid)
            })
            return result.to_response()


view = LoginAPI
