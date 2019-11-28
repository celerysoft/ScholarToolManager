# -*- coding: utf-8 -*-
from application import exception
from application.model.user import User
from application.util import authorization
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


class UserPasswordAPI(BaseNeedLoginAPI):
    methods = ['PUT']

    def put(self):
        old_password = self.get_post_data('old_password', require=True, error_message='请输入旧密码')
        password = self.get_post_data('password', require=True, error_message='请输入密码')

        with session_scope() as session:
            user = session.query(User).filter(User.uuid == self.user_uuid).first()
            if user is None:
                raise exception.api.Unauthorized('请先登录')

            hashed_old_password = authorization.toolkit.hash_plaintext(old_password)
            if hashed_old_password == user.password:
                user.password = authorization.toolkit.hash_plaintext(password)

            return ApiResult('修改密码成功', 201).to_response()


view = UserPasswordAPI
