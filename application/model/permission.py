# -*- coding: utf-8 -*-
from enum import Enum

from sqlalchemy import Column
from sqlalchemy.dialects.mysql import VARCHAR, TEXT

from application.model.base_model import Base, BaseModelMixin


class Permission(Base, BaseModelMixin):
    __tablename__ = 'permission'
    __comment__ = '权限表'

    name = Column(VARCHAR(36), nullable=False, comment='权限名')
    label = Column(VARCHAR(64), nullable=False, comment='权限描述')
    description = Column(TEXT, comment='权限描述')

    class Status(Enum):
        INITIALIZATION = 0
        VALID = 1
        DELETED = 2
        INVALID = 3

    class PermissionLabel(Enum):
        LOGIN = 'login'
        MANAGEMENT = 'management'

    def __init__(self, name, label, description, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.name = name
        self.label = label
        self.description = description
        self.status = self.Status.VALID.value


cacheable = Permission
