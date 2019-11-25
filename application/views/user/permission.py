# -*- coding: utf-8 -*-
from flask import make_response

from application.model.legacy.model import to_dict
from application.util import permission
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


class PermissionAPI(BaseNeedLoginAPI):
    methods = ['GET']

    def get(self):
        with session_scope() as db_session:
            permissions = permission.toolkit.derive_user_permissions(db_session, self.user_id)
            permission_list = []
            for p in permissions:
                permission_list.append(to_dict(p))

        result = ApiResult('获取用户权限成功', payload={
            'permissions': permission_list
        })
        return make_response(result.to_response())


view = PermissionAPI
