# -*- coding: utf-8 -*-
import hashlib
from datetime import datetime

from flask import session, make_response

import configs
from application import exception
from application.model.model import User, Role, UserRole, to_dict
from application.util import permission
from application.util.database import session_scope
from application.views.base_api import BaseAPI, ApiResult


class LoginAPI(BaseAPI):
    methods = ['POST']

    def post(self):
        name = self.get_post_data('name', require=True, error_message='请输入用户名或邮箱')
        password = self.get_post_data('password', require=True, error_message='请输入密码')

        with session_scope() as db_session:
            user = db_session.query(User).filter(User.username == name).first()  # type:User
            if user is None:
                user = db_session.query(User).filter(User.email == name).first()
                if user is None:
                    raise exception.api.NotFound('用户不存在')
    
            # check password
            salt = configs.SHA1_SALT

            sha1 = hashlib.sha1()
            sha1.update(salt.encode('utf-8'))
            sha1.update(b':')
            sha1.update(password.encode('utf-8'))
            if user.password != sha1.hexdigest():
                raise exception.api.InvalidRequest('密码错误，请重试')

            if not permission.toolkit.check_login_permission(db_session, user.id):
                user_role = db_session.query(UserRole).filter(UserRole.user_id == user.id).first()
                if user_role is None:
                    user_role = UserRole(user.id, Role.USER)
                    db_session.add(user_role)
                else:
                    raise exception.api.Forbidden('该用户已被拉黑，请联系管理员进行申诉')
    
            user.last_login_at = datetime.now().timestamp()

            session['user'] = to_dict(user)

            result = ApiResult('登录成功')
            return make_response(result.to_response())


view = LoginAPI
