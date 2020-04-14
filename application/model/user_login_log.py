# -*- coding: utf-8 -*-
from enum import Enum

from sqlalchemy import Column, String

from application.model.base_model import Base, BaseModelMixin


class UserLoginLog(Base, BaseModelMixin):
    __tablename__ = 'user_login_log'
    __comment__ = '用户登录日志'

    user_uuid = Column(String(32), nullable=False, comment='用户UUID')
    ip = Column(String(64), nullable=False, comment='登录IP')

    class STATUS(Enum):
        INACTIVATED = 0
        ACTIVATED = 1
        DELETED = 2

    def __init__(self, user_uuid, ip, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user_uuid = user_uuid
        self.ip = ip
        self.status = 1


cacheable = UserLoginLog
