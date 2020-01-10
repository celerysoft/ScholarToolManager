# -*- coding: utf-8 -*-
from flask import make_response

from application import exception
from application.model.legacy.model import Role, Permission, to_dict, RolePermission
from application.util import permission
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


# TODO 移至后台管理接口
class PermissionAPI(BaseNeedLoginAPI):
    methods = ['GET']

    def get(self):
        role_id = self.get_data('role_id')
        return_all_permissions = self.get_data('all_permissions')

        with session_scope() as db_session:
            if not permission.toolkit.check_manage_role_permission(db_session, self.user_id):
                raise exception.api.Forbidden('当前用户无权进行角色权限管理')

            all_permission_list = None
            if return_all_permissions:
                all_permission_list = []
                all_permissions = db_session.query(Permission).all()
                for p in all_permissions:
                    all_permission_list.append(to_dict(p))

            data = None
            if self.valid_data(role_id):
                role = db_session.query(Role).filter(Role.id == role_id).first()

                permissions = db_session.query(Permission) \
                    .filter(Role.id == RolePermission.role_id) \
                    .filter(RolePermission.permission_id == Permission.id) \
                    .filter(Role.id == role_id)
                permission_list = []
                for p in permissions:
                    permission_list.append(to_dict(p))
                data = {
                    'role_id': role_id,
                    'role_name': role.name,
                    'role_label': role.label,
                    'role_description': role.description,
                    'permissions': permission_list
                }

        payload = data if data is not None else {}
        if all_permission_list is not None:
            payload['all_permissions'] = all_permission_list
        result = ApiResult('获取权限信息成功', payload=payload)
        return make_response(result.to_response())


view = PermissionAPI
