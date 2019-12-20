# -*- coding: utf-8 -*-
from application.model.user import User
from application.util.database import session_scope
from application.views.base_api import PermissionRequiredAPI, ApiResult


class ManagementUserAPI(PermissionRequiredAPI):
    methods = ['GET']
    need_login_methods = ['GET']
    permission_required_methods = ['GET']
    permission_required_for_get = []

    def get(self):
        with session_scope() as session:
            user_list = []
            query = self.derive_query_for_get_method(session, User)
            page, page_size, offset, max_page = self.derive_page_parameter(query.count())
            users = query.offset(offset).limit(page_size).all()
            for user in users:  # type: User
                user_list.append(user.to_dict())

            result = ApiResult('获取用户信息成功', payload={
                'users': user_list,
                'page': page,
                'page_size': page_size,
                'max_page': max_page,
            })
            return result.to_response()


view = UserAPI
