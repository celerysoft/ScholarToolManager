# -*- coding: utf-8 -*-
from jwt import PyJWTError

import configs
from application import exception
from application.model.user import User
from application.util import authorization, background_task
from application.util.constant import JwtSub
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


class UserEmailAPI(BaseNeedLoginAPI):
    methods = ['PUT', 'PATCH']

    def put(self):
        jwt = self.get_post_data('jwt')
        if self.valid_data(jwt):
            return self.modify_email(jwt)

    def modify_email(self, jwt):
        try:
            jwt_dict = authorization.toolkit.decode_jwt_token(jwt)  # type:dict
        except PyJWTError:
            raise exception.api.InvalidRequest('修改电子邮件地址的链接已过期或者激活请求非法')

        if 'sub' not in jwt_dict.keys() or jwt_dict['sub'] != JwtSub.ModifyEmail.value:
            raise exception.api.InvalidRequest('修改电子邮件地址的请求非法')

        if 'uuid' not in jwt_dict.keys() or 'email' not in jwt_dict.keys():
            raise exception.api.InvalidRequest('修改电子邮件地址的请求非法')

        uuid = jwt_dict['uuid']
        with session_scope() as session:
            user = session.query(User).filter(User.uuid == uuid).first()

            email = jwt_dict['email']
            if user.email == email:
                raise exception.api.Conflict('电子邮箱地址已经成功完成了变更，无法重复变更')

            user.email = email

            jwt_token = authorization.toolkit.derive_jwt_token(uuid)
            result = ApiResult('电子邮箱地址修改成功', 201, payload={
                'jwt': jwt_token
            })
            return result.to_response()

    def patch(self):
        email = self.get_post_data('email')
        if self.valid_data(email):
            return self.send_activation_email_for_modifying_email_address(email)
        else:
            return self.send_activation_email()

    def send_activation_email_for_modifying_email_address(self, email):
        with session_scope() as session:
            password = self.get_post_data('password', require=True, error_message='请输入密码以进行校验')
            hashed_password = authorization.toolkit.hash_plaintext(password)
            user = session.query(User).filter(User.uuid == self.user_uuid).first()
            if user.email == email:
                raise exception.api.Conflict('新电子邮箱地址不能和当前的一致')
            if user.password != hashed_password:
                raise exception.api.InvalidRequest('密码错误，无法完成电子邮箱地址的修改')

            email_count = session.query(User).filter(User.email == email,
                                                     User.status != User.STATUS.DELETED).count()
            if email_count > 0:
                raise exception.api.Conflict('该电子邮箱地址已被其他用户占用')

            expired_in = 48
            extra_payload = {
                'sub': JwtSub.ModifyEmail.value,
                'email': email,
            }
            jwt = authorization.toolkit.derive_jwt_token(self.user_uuid, expired_in, extra_payload)
            if configs.DEBUG:
                domain = 'http://localhost:8080'
            else:
                domain = 'http://www.celerysoft.science'
            activate_url = '{}/account/email?jwt={}'.format(domain, jwt)

            background_task.send_activation_email_for_modifying_email_address.delay(user_email=email,
                                                                                    username=user.username,
                                                                                    activate_url=activate_url)

            return ApiResult('验证邮件已发送至新邮箱{}，请查收'.format(user.email), 201).to_response()

    def send_activation_email(self):
        with session_scope() as session:
            user = session.query(User).filter(User.uuid == self.user_uuid).first()

            expired_in = 48
            extra_payload = {
                'sub': JwtSub.Activation.value
            }
            jwt = authorization.toolkit.derive_jwt_token(self.user_uuid, expired_in, extra_payload)
            if configs.DEBUG:
                domain = 'http://localhost:8080'
            else:
                domain = 'http://www.celerysoft.science'
            activate_url = '{}/activation?jwt={}'.format(domain, jwt)

            background_task.send_activation_email.delay(user_email=user.email,
                                                        username=user.username,
                                                        activate_url=activate_url)

            return ApiResult('激活邮件已发送至注册邮箱{}，请查收'.format(user.email), 201).to_response()


view = UserEmailAPI
