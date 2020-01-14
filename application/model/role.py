# -*- coding: utf-8 -*-
from enum import Enum

from sqlalchemy import Column
from sqlalchemy.dialects.mysql import VARCHAR, TEXT

from application.model.base_model import Base, BaseModelMixin


class BuiltInRoleObject(object):
    def __init__(self, name, description):
        self.name = name
        self.description = description


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

    class BuiltInRole(Enum):
        REGISTRATION_USER = BuiltInRoleObject('注册会员', '注册会员')
        ADMINISTRATOR = BuiltInRoleObject('超级管理员', '超级管理员')
        BAN_LIST = BuiltInRoleObject('小黑屋', '小黑屋')

    def __init__(self, name, description, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.name = name
        self.description = description
        self.status = self.Status.VALID.value


cacheable = Role
