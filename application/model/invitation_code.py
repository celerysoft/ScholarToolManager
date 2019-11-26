# -*- coding: utf-8 -*-
from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import VARCHAR, DATETIME

from application.model.base_model import Base, BaseModelMixin


class InvitationCode(Base, BaseModelMixin):
    __tablename__ = 'invitation_code'
    __comment__ = '邀请码'

    code = Column(String)
    inviter_uuid = Column(VARCHAR(36))
    invitee_uuid = Column(VARCHAR(36))
    invited_at = Column(DATETIME)

    def __init__(self, code, inviter_uuid, *args, **kwargs):
        super().__init__()

        self.code = code
        self.inviter_uuid = inviter_uuid


cacheable = InvitationCode
