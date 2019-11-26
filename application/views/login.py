# -*- coding: utf-8 -*-
from application import exception
from application.model.user import User
from application.util import authorization
from application.util.database import session_scope
from application.views.base_api import BaseAPI, ApiResult


class LoginAPI(BaseAPI):
    methods = ['POST']

    def post(self):
        username = self.get_post_data('username', require=True, error_message='请输入用户名或邮箱')
        password = self.get_post_data('password', require=True, error_message='请输入密码')

        with session_scope() as session:
            user = session.query(User).filter(User.username == username).first()  # type:User
            if user is None:
                user = session.query(User).filter(User.email == username).first()
                if user is None:
                    raise exception.api.NotFound('用户不存在')

                hashed_password = authorization.toolkit.hash_plaintext(password)

                if user.password != hashed_password:
                    raise exception.api.InvalidRequest('密码错误，请重试')

                #     if not permission.toolkit.check_login_permission(db_session, user.id):
                #         user_role = db_session.query(UserRole).filter(UserRole.user_id == user.id).first()
                #         if user_role is None:
                #             user_role = UserRole(user.id, Role.USER)
                #             db_session.add(user_role)
                #         else:
                #             raise exception.api.Forbidden('该用户已被拉黑，请联系管理员进行申诉')
                #
                #     user.last_login_at = datetime.now().timestamp()

            result = ApiResult('登录成功', payload={
                'jwt': authorization.toolkit.derive_jwt_token(user.uuid)
            })
            return result.to_response()


view = LoginAPI
