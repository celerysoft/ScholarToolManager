# -*- coding: utf-8 -*-
from jwt import PyJWTError

import configs
from application import exception
from application.model.user import User
from application.util import authorization, background_task
from application.util.constant import JwtSub
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult, jwt_api


class UserPasswordAPI(BaseNeedLoginAPI):
    methods = ['PUT', 'PATCH']
    need_login_methods = []

    def put(self):
        jwt = self.get_post_data('jwt')
        if self.valid_data(jwt):
            return self.reset_password(jwt)
        else:
            return self.update_password()

    def reset_password(self, jwt: str):
        """
        重设密码

        :return:
        """
        password = self.get_post_data('password', require=True, error_message='请输入新密码')
        try:
            jwt_dict = authorization.toolkit.decode_jwt_token(jwt)  # type:dict
        except PyJWTError:
            raise exception.api.InvalidRequest('重设密码的链接已过期或者重设密码请求非法')

        if 'sub' not in jwt_dict.keys() or jwt_dict['sub'] != JwtSub.ResetPassword.value:
            raise exception.api.InvalidRequest('重设密码的请求非法')

        if 'uuid' not in jwt_dict.keys():
            raise exception.api.InvalidRequest('重设密码的请求非法')

        uuid = jwt_dict['uuid']
        with session_scope() as session:
            user = session.query(User).filter(User.uuid == uuid).first()

            user.password = authorization.toolkit.hash_plaintext(password)

            result = ApiResult('密码重设成功，以后请使用新密码登录', 201)
            return result.to_response()

    @jwt_api
    def update_password(self):
        """
        修改密码

        :return:
        """
        old_password = self.get_post_data('old_password', require=True, error_message='请输入旧密码')
        password = self.get_post_data('password', require=True, error_message='请输入密码')

        with session_scope() as session:
            user = session.query(User).filter(User.uuid == self.user_uuid).first()
            if user is None:
                raise exception.api.Unauthorized('请先登录')

            hashed_old_password = authorization.toolkit.hash_plaintext(old_password)
            if hashed_old_password != user.password:
                raise exception.api.InvalidRequest('旧密码错误')

            user.password = authorization.toolkit.hash_plaintext(password)
            return ApiResult('修改密码成功', 201).to_response()

    def patch(self):
        """
        发送重设密码的邮件

        :return:
        """
        email = self.get_post_data('email', require=True, error_message='请输入电子邮箱地址')

        with session_scope() as session:
            user = session.query(User).filter(User.email == email).first()  # type: User
            if user is None:
                raise exception.api.NotFound('未找到使用该电子邮箱地址进行注册的用户')
            if user.status == User.STATUS.INACTIVATED:
                raise exception.api.Forbidden('该电子邮箱地址尚未完成验证，无法进行密码找回，请尝试重新注册或者联系客服解决')
            if user.status == User.STATUS.SUSPENDED:
                raise exception.api.Forbidden('该电子邮箱地址关联的账号已被停用，如需重新启用账号，请联系客服')

            expired_in = 1
            extra_payload = {
                'sub': JwtSub.ResetPassword.value,
            }
            jwt = authorization.toolkit.derive_jwt_token(
                user.id, user.uuid, expired_in, extra_payload
            )
            if configs.DEBUG:
                domain = 'http://localhost:8080'
            else:
                domain = 'http://www.celerysoft.science'
            reset_password_url = '{}/password-reset/password?jwt={}'.format(domain, jwt)

            background_task.send_reset_password_email.delay(
                user_email=email,
                username=user.username,
                reset_password_url=reset_password_url
            )

            return ApiResult('重设密码的邮件已发送至{}，请查收'.format(user.email), 201).to_response()


view = UserPasswordAPI
