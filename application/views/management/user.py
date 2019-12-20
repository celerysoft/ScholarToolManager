# -*- coding: utf-8 -*-
from application import exception
from application.model.user import User
from application.util.database import session_scope
from application.views.base_api import PermissionRequiredAPI, ApiResult


class ManagementUserAPI(PermissionRequiredAPI):
    methods = ['GET']
    need_login_methods = ['GET']
    permission_required_methods = ['GET']
    permission_required_for_get = []

    def get(self):
        user_uuid = self.get_data('uuid')
        if self.valid_data(user_uuid):
            return self.get_single_user(user_uuid)

        with session_scope() as session:
            user_list = []
            query = self.derive_query_for_get_method(session, User) \
                .filter(User.status != User.STATUS.DELETED)
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

    def get_single_user(self, user_uuid):
        with session_scope() as session:
            user = session.query(User) \
                .filter(User.uuid == user_uuid,
                        User.status != User.STATUS.DELETED).first()  # type: User

            if user is None:
                raise exception.api.NotFound('用户不存在')

            result = ApiResult('获取用户信息成功', payload={
                'user': user.to_dict()
            })
            return result.to_response()


view = ManagementUserAPI
