# -*- coding: utf-8 -*-
from flask import request

from application import exception
from application.model.invitation_code import InvitationCode
from application.model.user import User
from application.util.database import session_scope
from application.views.base_api import PermissionRequiredAPI, ApiResult


class ManagementInvitationAPI(PermissionRequiredAPI):
    methods = ['GET', 'POST']
    permission_required_for_get = []
    permission_required_for_post = []

    def get(self):
        with session_scope() as session:
            invitation_list = []
            query = self.derive_query_for_get_method(session, InvitationCode) \
                .filter(User.status != User.STATUS.DELETED)
            page, page_size, offset, max_page = self.derive_page_parameter(query.count())
            invitations = query.offset(offset).limit(page_size).all()
            for invitation in invitations:  # type: InvitationCode
                invitation_dict = invitation.to_dict()
                inviter_username = session.query(User.username) \
                    .filter(User.uuid == invitation.inviter_uuid,
                            User.status != User.STATUS.DELETED).first()
                inviter_username = inviter_username.username if inviter_username is not None else ''
                invitee_username = session.query(User.username) \
                    .filter(User.uuid == invitation.invitee_uuid,
                            User.status != User.STATUS.DELETED).first()
                invitee_username = invitee_username.username if invitee_username is not None else ''
                invitation_dict['inviter_username'] = inviter_username
                invitation_dict['invitee_username'] = invitee_username
                invitation_list.append(invitation_dict)

            result = ApiResult('获取邀请码信息成功', payload={
                'invitations': invitation_list,
                'page': page,
                'page_size': page_size,
                'max_page': max_page,
            })
            return result.to_response()

    def post(self):
        with session_scope() as session:
            invitation = InvitationCode(self.user_uuid)
            session.add(invitation)
            session.flush()

            result = ApiResult('创建邀请码成功', payload={
                'invitation': invitation.to_dict(),
            })
            return result.to_response()


view = ManagementInvitationAPI
