# -*- coding: utf-8 -*-
from enum import Enum

from sqlalchemy import Column
from sqlalchemy.dialects.mysql import VARCHAR, TEXT

from application.model.base_model import Base, BaseModelMixin


class Role(Base, BaseModelMixin):
    __tablename__ = 'role'
    __comment__ = '角色表'

    name = Column(VARCHAR(36), nullable=False, comment='角色名')
    description = Column(TEXT, comment='角色描述')

    class Status(Enum):
        INITIALIZATION = 0
        VALID = 1
        DELETED = 2
        INVALID = 3

    class RoleName(Enum):
        REGISTRATION_USER = '注册会员'
        ADMINISTRATOR = '超级管理员'
        BAN_LIST = '小黑屋'

    def __init__(self, name, description, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.name = name
        self.description = description
        self.status = self.Status.VALID.value


cacheable = Role
