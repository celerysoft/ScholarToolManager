# -*- coding: utf-8 -*-
import random

from flask import make_response

from application import exception
from application.model.legacy.model import InvitationCode
from application.util import permission
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


class InvitationCodeAPI(BaseNeedLoginAPI):
    methods = ['POST']

    @classmethod
    def derive_invitation_code(cls):
        seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+=-"
        codes = []
        for i in range(32):
            codes.append(random.choice(seed))
        invitation_code = ''.join(codes)
        return invitation_code

    def post(self):
        with session_scope() as session:
            if not permission.toolkit.check_manage_invitation_code_permission(session, self.user_id):
                raise exception.api.Forbidden('当前用户无权创建邀请码')

            while True:
                invitation_code = self.derive_invitation_code()
                invitation = session.query(InvitationCode) \
                    .filter(InvitationCode.code == invitation_code).first()
                if invitation is None:
                    break

            invitation = InvitationCode(invitation_code, self.user_id)
            session.add(invitation)

        result = ApiResult('生成邀请码成功', 201, {
            'code': invitation_code
        })
        return make_response(result.to_response())


view = InvitationCodeAPI
