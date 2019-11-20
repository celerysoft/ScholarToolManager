# -*- coding: utf-8 -*-
import hashlib
import re
from datetime import datetime

from flask import session, make_response

import configs
from application import exception
from application.model.model import User, Role, UserRole, to_dict, InvitationCode, UserScholarBalance
from application.util.database import session_scope
from application.views.base_api import BaseAPI, ApiResult


class RegisterAPI(BaseAPI):
    methods = ['POST']

    def post(self):
        re_email = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')

        username = self.get_post_data('name', require=True, error_message='请输入用户名')
        email = self.get_post_data('email', require=True, error_message='请输入邮箱')
        if not re_email.match(email):
            raise exception.api.InvalidRequest('请输入正确的邮箱')
        password = self.get_post_data('password', require=True, error_message='请输入密码')
        code = self.get_post_data('invitation_code', require=True, error_message='请输入邀请码')

        with session_scope() as db_session:
            user = db_session.query(User).filter(User.username == username).first()
            if user is not None:
                raise exception.api.Conflict('用户名已被注册')
            user = db_session.query(User).filter(User.email == email).first()
            if user is not None:
                return exception.api.Conflict('邮箱已被注册')

            invitation_code = db_session.query(InvitationCode).filter(InvitationCode.code == code).first()
            if invitation_code is None:
                raise exception.api.NotFound('邀请码不存在')
            elif not invitation_code.available:
                raise exception.api.Conflict('邀请码已被使用')

            # 将记录写入user表
            salt = configs.SHA1_SALT
            sha1_password = '{}:{}'.format(salt, password)
            user = User(username=username.strip(), email=email, name=username.strip(),
                        password=hashlib.sha1(sha1_password.encode('utf-8')).hexdigest(),
                        image='https://api.adorable.io/avatars/285/%s.png' % hashlib.md5(
                            email.encode('utf-8')).hexdigest())

            db_session.add(user)
            db_session.flush()

            session['user'] = to_dict(user)

            # 将记录写入user_role表
            user_role = UserRole(user.id, Role.USER)
            db_session.add(user_role)

            # 将记录写入invitation_code表
            invitation_code.available = False
            invitation_code.invitee_id = user.id
            invitation_code.invited_at = datetime.now().timestamp()

            # 将记录写入user_scholar_balance表
            scholar_balance_for_new_user = configs.NEW_USER_SCHOLAR_BALANCE
            user_scholar_balance = UserScholarBalance(user.id, scholar_balance_for_new_user)
            db_session.add(user_scholar_balance)

            result = ApiResult('注册成功', status=201)
            return make_response(result.to_response())


view = RegisterAPI
