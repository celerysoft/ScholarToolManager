# -*- coding: utf-8 -*-
import re
from datetime import datetime

from flask import Blueprint
from jwt import PyJWTError

import configs
from app import derive_import_root, add_url_rules_for_blueprint
from application import exception
from application.model.invitation_code import InvitationCode
from application.model.role import Role
from application.model.scholar_payment_account import ScholarPaymentAccount
from application.model.user import User
from application.model.user_role import UserRole
from application.util import authorization, background_task
from application.util.constant import JwtSub
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


class UserAPI(BaseNeedLoginAPI):
    methods = ['GET', 'POST', 'PUT']
    need_login_methods = ['GET']

    def get(self):
        uuid = self.get_data('uuid')
        if self.valid_data(uuid):
            return self.get_user_information(uuid)
        return self.get_self_information()

    def get_self_information(self):
        with session_scope() as session:
            user = session.query(User).filter(User.uuid == self.user_uuid).first()  # type:User

            result = ApiResult('获取个人信息成功', payload={
                'uuid': user.uuid,
                'username': user.username,
                'email': user.email,
                'register_date': user.created_at.isoformat(),
                'created_at': user.created_at.isoformat(),
                'status': user.status
            })
            return result.to_response()

    def get_user_information(self, uuid):
        with session_scope() as session:
            user = session.query(User).filter(User.uuid == uuid).first()  # type:User

            payload = {
                'uuid': user.uuid,
                'username': user.username,
                'email': user.email,
                'register_date': user.created_at.isoformat(),
                'created_at': user.created_at.isoformat(),
                'status': user.status
            }
            if self.user_uuid != uuid:
                payload['email'] = ''
                payload['status'] = -1
            result = ApiResult('获取个人信息成功', payload=payload)
            return result.to_response()

    def post(self):
        re_email = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')

        username = self.get_post_data('username', require=True, error_message='请输入用户名')
        email = self.get_post_data('email', require=True, error_message='请输入邮箱')
        if not re_email.match(email):
            raise exception.api.InvalidRequest('请输入正确的邮箱')
        password = self.get_post_data('password', require=True, error_message='请输入密码')
        code = self.get_post_data('invitation_code', require=True, error_message='请输入邀请码')

        with session_scope() as session:
            user = session.query(User).filter(User.username == username, User.status != User.STATUS.DELETED).first()
            if user is not None:
                raise exception.api.Conflict('用户名已被注册')
            user = session.query(User).filter(User.email == email, User.status != User.STATUS.DELETED).first()
            if user is not None:
                return exception.api.Conflict('邮箱已被注册')

            invitation_code = session.query(InvitationCode) \
                .filter(InvitationCode.code == code).first()  # type:InvitationCode
            if invitation_code is None:
                raise exception.api.NotFound('邀请码不存在')
            elif invitation_code.status != 1:
                raise exception.api.Conflict('邀请码已被使用')

            # 将记录写入user表
            hashed_password = authorization.toolkit.hash_plaintext(password)
            user = User(username=username.strip(), email=email, password=hashed_password)  # type: User

            session.add(user)
            session.flush()

            # 进行角色关联
            role = session.query(Role).filter(Role.name == Role.BuiltInRole.REGISTRATION_USER.value.name,
                                              Role.status == Role.Status.VALID.value).first()  # type: Role
            user_role = UserRole(user_uuid=user.uuid, role_uuid=role.uuid)
            session.add(user_role)

            # 将记录写入invitation_code表
            invitation_code.status = 2
            invitation_code.invitee_uuid = user.uuid
            invitation_code.invited_at = datetime.now()

            # 创建学术积分账户
            scholar_payment_account = ScholarPaymentAccount(
                user_uuid=user.uuid,
                balance=0,
            )
            session.add(scholar_payment_account)

            self.send_activation_email(user)

            result = ApiResult('注册成功', status=201, payload={
                'jwt': authorization.toolkit.derive_jwt_token(user.uuid)
            })
            return result.to_response()

    def send_activation_email(self, user: User):
        expired_in = 48
        extra_payload = {
            'sub': 'activation'
        }
        jwt = authorization.toolkit.derive_jwt_token(user.uuid, expired_in, extra_payload)
        if configs.DEBUG:
            domain = 'http://localhost:8080'
        else:
            domain = 'http://www.celerysoft.science'
        activate_url = '{}/activation?jwt={}'.format(domain, jwt)

        background_task.send_activation_email.delay(user_email=user.email,
                                                    username=user.username,
                                                    activate_url=activate_url)

    def put(self):
        jwt = self.get_post_data('jwt')
        if self.valid_data(jwt):
            return self.validate_email(jwt)

    def validate_email(self, jwt):
        try:
            jwt_dict = authorization.toolkit.decode_jwt_token(jwt)  # type:dict
        except PyJWTError:
            raise exception.api.InvalidRequest('激活链接已过期或者激活请求非法')

        if 'sub' not in jwt_dict.keys() or jwt_dict['sub'] != JwtSub.Activation.value:
            raise exception.api.InvalidRequest('激活请求非法')

        uuid = jwt_dict['uuid']
        with session_scope() as session:
            user = session.query(User).filter(User.uuid == uuid).first()
            if user.status == 1:
                raise exception.api.Conflict('邮箱已完成验证，无需重复验证')

            user.status = 1

            scholar_payment_account = session.query(ScholarPaymentAccount) \
                .filter(ScholarPaymentAccount.user_uuid == uuid,
                        ScholarPaymentAccount.status == ScholarPaymentAccount.STATUS.VALID.value) \
                .first()  # type: ScholarPaymentAccount
            if scholar_payment_account is not None:
                scholar_payment_account.balance = configs.NEW_USER_SCHOLAR_BALANCE

            jwt_token = authorization.toolkit.derive_jwt_token(uuid)
            result = ApiResult('邮箱验证成功', 201, payload={
                'jwt': jwt_token
            })
            return result.to_response()


view = UserAPI

bp = Blueprint(__name__.split('.')[-1], __name__)
root = derive_import_root(__name__)
add_url_rules_for_blueprint(root, bp)
