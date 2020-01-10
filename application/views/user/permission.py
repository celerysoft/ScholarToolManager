# -*- coding: utf-8 -*-
from flask import make_response

from application.model.permission import Permission
from application.util import permission
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


class UserPermissionAPI(BaseNeedLoginAPI):
    methods = ['GET']

    def get(self):
        with session_scope() as db_session:
            permissions = permission.toolkit.derive_user_permissions(db_session, self.user_uuid)
            permission_list = []
            for p in permissions:  # type: Permission
                permission_list.append(p.to_dict())

        result = ApiResult('获取用户权限成功', payload={
            'permissions': permission_list
        })
        return make_response(result.to_response())


view = UserPermissionAPI
