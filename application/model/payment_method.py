# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import VARCHAR

from application.model.base_model import Base, BaseModelMixin


class PaymentMethod(Base, BaseModelMixin):
    __tablename__ = 'payment_method'
    __comment__ = '支付渠道'

    name = Column(VARCHAR(32), nullable=False, comment='渠道名')

    class STATUS(object):
        INITIALIZATION = 0
        VALID = 1
        DELETED = 2

    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.name = name
        self.status = 1


cacheable = PaymentMethod
