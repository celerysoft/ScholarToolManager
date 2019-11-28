# -*- coding: utf-8 -*-
from flask import Blueprint
from jwt import PyJWTError

from app import derive_import_root, add_url_rules_for_blueprint
from application import exception
from application.model.user import User
from application.util import authorization
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


class UserAPI(BaseNeedLoginAPI):
    methods = ['GET', 'PUT']
    need_login_methods = ['GET']

    def get(self):
        with session_scope() as session:
            user = session.query(User).filter(User.uuid == self.user_uuid).first()  # type:User

            result = ApiResult('获取个人信息成功', payload={
                'uuid': user.uuid,
                'username': user.username,
                'email': user.email,
                'register_date': user.created_at.isoformat(),
                'status': user.status
            })
            return result.to_response()

    def put(self):
        jwt = self.get_post_data('jwt')
        if self.valid_data(jwt):
            return self.validate_email(jwt)

    def validate_email(self, jwt):
        try:
            jwt_dict = authorization.toolkit.decode_jwt_token(jwt)  # type:dict
        except PyJWTError:
            raise exception.api.InvalidRequest('激活链接已过期或者激活请求非法')

        if 'sub' not in jwt_dict.keys() or jwt_dict['sub'] != 'activation':
            raise exception.api.InvalidRequest('激活请求非法')

        uuid = jwt_dict['uuid']
        with session_scope() as session:
            user = session.query(User).filter(User.uuid == uuid).first()
            if user.status == 1:
                raise exception.api.Conflict('邮箱已完成验证，无需重复验证')

            user.status = 1

            jwt_token = authorization.toolkit.derive_jwt_token(uuid)
            result = ApiResult('邮箱验证成功', 201, payload={
                'jwt': jwt_token
            })
            return result.to_response()


view = UserAPI

bp = Blueprint(__name__.split('.')[-1], __name__)
root = derive_import_root(__name__)
add_url_rules_for_blueprint(root, bp)
