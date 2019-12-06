# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import VARCHAR, INTEGER

from application.model.base_model import Base, BaseModelMixin


class UserAccount(Base, BaseModelMixin):
    __tablename__ = 'user_account'
    __comment__ = '用户账户'

    user_uuid = Column(VARCHAR(36), nullable=False, comment='账户持有人UUID')
    balance = Column(INTEGER, default=0, comment='账户余额')

    class STATUS(object):
        INITIALIZATION = 0
        VALID = 1
        DELETED = 2

    def __init__(self, user_uuid, balance, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user_uuid = user_uuid
        self.balance = balance
        self.status = 1


cacheable = UserAccount
