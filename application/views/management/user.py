# -*- coding: utf-8 -*-
from application import exception
from application.model.user import User
from application.model.user_login_log import UserLoginLog
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
            record_count = query.count()
            page, page_size, offset, max_page = self.derive_page_parameter(record_count)
            users = query.offset(offset).limit(page_size).all()
            for user in users:  # type: User
                user_object = user.to_dict()

                user_login_log = session.query(UserLoginLog).filter(
                    UserLoginLog.user_uuid == user.uuid,
                    UserLoginLog.status == UserLoginLog.STATUS.ACTIVATED.value).order_by(
                    UserLoginLog.created_at.desc()).first()  # type: UserLoginLog
                if user_login_log is None:
                    user_object['last_login_at'] = user.created_at.isoformat()
                else:
                    user_object['last_login_at'] = user_login_log.created_at.isoformat()

                user_list.append(user_object)

            result = ApiResult('获取用户信息成功', payload={
                'users': user_list,
                'page': page,
                'page_size': page_size,
                'max_page': max_page,
                'total': record_count,
            })
            return result.to_response()

    def get_single_user(self, user_uuid):
        with session_scope() as session:
            user = session.query(User) \
                .filter(User.uuid == user_uuid,
                        User.status != User.STATUS.DELETED).first()  # type: User

            if user is None:
                raise exception.api.NotFound('用户不存在')

            user_object = user.to_dict()

            user_login_log = session.query( UserLoginLog).filter(
                UserLoginLog.user_uuid == user.uuid,
                UserLoginLog.status == UserLoginLog.STATUS.ACTIVATED.value).order_by(
                UserLoginLog.created_at.desc()).first()  # type: UserLoginLog
            if user_login_log is None:
                user_object['last_login_at'] = user.created_at.isoformat()
            else:
                user_object['last_login_at'] = user_login_log.created_at.isoformat()

            result = ApiResult('获取用户信息成功', payload={
                'user': user_object
            })
            return result.to_response()


view = ManagementUserAPI
