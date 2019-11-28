# -*- coding: utf-8 -*-
import configs
from application import exception
from application.model.user import User
from application.util import authorization, background_task
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


class UserEmailAPI(BaseNeedLoginAPI):
    methods = ['PUT', 'PATCH']

    def put(self):
        raise exception.api.ServiceUnavailable('修改电子邮箱的接口建设中')

    def patch(self):
        with session_scope() as session:
            user = session.query(User).filter(User.uuid == self.user_uuid).first()

            expired_in = 48
            extra_payload = {
                'sub': 'activation'
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
