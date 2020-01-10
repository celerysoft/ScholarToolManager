# -*- coding: utf-8 -*-
from enum import Enum

from sqlalchemy import Column
from sqlalchemy.dialects.mysql import VARCHAR

from application.model.base_model import Base, BaseModelMixin


class UserRole(Base, BaseModelMixin):
    __tablename__ = 'user_role'
    __comment__ = '用户角色表'

    user_uuid = Column(VARCHAR(36), nullable=False, comment='用户UUID')
    role_uuid = Column(VARCHAR(36), nullable=False, comment='角色UUID')

    class Status(Enum):
        INITIALIZATION = 0
        VALID = 1
        DELETED = 2
        INVALID = 3

    def __init__(self, user_uuid, role_uuid, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user_uuid = user_uuid
        self.role_uuid = role_uuid
        self.status = self.Status.VALID.value


cacheable = UserRole
