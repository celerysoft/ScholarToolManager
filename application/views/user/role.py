# -*- coding: utf-8 -*-
from flask import make_response

from application import exception
from application.model.model import User, UserRole, Role
from application.util import permission
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


class UserRoleAPI(BaseNeedLoginAPI):
    methods = ['PATCH']

    def patch(self):
        target_user_id = self.get_post_data('user_id', require=True, error_message='缺少user_id字段')
        role_id = self.get_post_data('role_id', require=True, error_message='缺少role_id字段')

        with session_scope() as db_session:
            if not permission.toolkit.check_manage_role_permission(db_session, self.user_id):
                raise exception.api.Forbidden('当前用户无法管理用户角色')

            user_role = db_session.query(UserRole) \
                .filter(User.id == UserRole.user_id) \
                .filter(UserRole.role_id == Role.id) \
                .filter(User.id == target_user_id).first()

            user_role.role_id = role_id

        result = ApiResult('修改用户角色成功')
        return make_response(result.to_response())


view = UserRoleAPI
