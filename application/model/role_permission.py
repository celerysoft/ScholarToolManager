# -*- coding: utf-8 -*-
from enum import Enum

from sqlalchemy import Column
from sqlalchemy.dialects.mysql import VARCHAR

from application.model.base_model import Base, BaseModelMixin


class RolePermission(Base, BaseModelMixin):
    __tablename__ = 'role_permission'
    __comment__ = '角色权限表'

    role_uuid = Column(VARCHAR(36), nullable=False, comment='角色UUID')
    permission_uuid = Column(VARCHAR(36), nullable=False, comment='权限UUID')

    class STATUS(Enum):
        INITIALIZATION = 0
        VALID = 1
        DELETED = 2
        INVALID = 3

    def __init__(self, role_uuid, permission_uuid, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.role_uuid = role_uuid
        self.permission_uuid = permission_uuid
        self.status = self.STATUS.VALID.value


cacheable = RolePermission
