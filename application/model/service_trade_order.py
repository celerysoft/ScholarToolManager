# -*- coding: utf-8 -*-
from enum import Enum

from sqlalchemy import Column
from sqlalchemy.dialects.mysql import VARCHAR

from application.model.base_model import Base, BaseModelMixin


class ServiceTradeOrder(Base, BaseModelMixin):
    __tablename__ = 'service_trade_order'
    __comment__ = '学术服务交易订单关系表'

    service_uuid = Column(VARCHAR(36), nullable=False, comment='学术服务UUID')
    trade_order_uuid = Column(VARCHAR(36), nullable=False, comment='交易订单UUID')

    class STATUS(Enum):
        # 状态：0 - 初始化，1 - 有效，2 - 作废
        INITIALIZATION = 0
        VALID = 1
        DELETED = 2

    def __init__(self, service_uuid: str, trade_order_uuid: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.service_uuid = service_uuid
        self.trade_order_uuid = trade_order_uuid

        self.status = 1


cacheable = ServiceTradeOrder
