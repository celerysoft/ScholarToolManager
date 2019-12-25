# -*- coding: utf-8 -*-
import uuid
from enum import Enum

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

    class Status(Enum):
        # 状态：0 - 初始化，1 - 有效，2 - 作废，3 - 已使用
        INITIALIZATION = 0
        VALID = 1
        DELETED = 2
        INVITED = 3

    def __init__(self, inviter_uuid, code=str(uuid.uuid4()), *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.code = code
        self.inviter_uuid = inviter_uuid


cacheable = InvitationCode
