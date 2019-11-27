# -*- coding: utf-8 -*-
import hashlib

from flask import make_response, Blueprint

import configs
from app import derive_import_root, add_url_rules_for_blueprint
from application import exception
from application.model.user import User
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


class UserAPI(BaseNeedLoginAPI):
    methods = ['GET', 'PATCH']
    need_login_methods = ['GET', 'PATCH']

    def get(self):
        with session_scope() as session:
            print('uuid: ', self.user_uuid)
            user = session.query(User).filter(User.uuid == self.user_uuid).first()  # type:User

            result = ApiResult('获取个人信息成功', payload={
                'uuid': user.uuid,
                'username': user.username,
                'email': user.email,
                'register_date': user.created_at.isoformat(),
                'status': user.status
            })
            return result.to_response()

    def patch(self):
        raise exception.api.ServiceUnavailable('接口建设中')
        # old_password = self.get_post_data('old_password', require=True, error_message='请输入原密码')
        # password = self.get_post_data('password', require=True, error_message='请输入新密码')
        #
        # with session_scope() as db_session:
        #
        #     user = db_session.query(User).filter(User.id == self.user_id).first()
        #
        #     sha1 = hashlib.sha1()
        #     sha1.update(configs.SHA1_SALT.encode('utf-8'))
        #     sha1.update(b':')
        #     sha1.update(old_password.encode('utf-8'))
        #     if user.password != sha1.hexdigest():
        #         raise exception.api.InvalidRequest('原密码错误，修改密码失败')
        #     else:
        #         sha1 = hashlib.sha1()
        #         sha1.update(configs.SHA1_SALT.encode('utf-8'))
        #         sha1.update(b':')
        #         sha1.update(password.encode('utf-8'))
        #         user.password = sha1.hexdigest()
        #
        # result = ApiResult('修改密码成功')
        # return make_response(result.to_response())


view = UserAPI

bp = Blueprint(__name__.split('.')[-1], __name__)
root = derive_import_root(__name__)
add_url_rules_for_blueprint(root, bp)
