# -*- coding: utf-8 -*-
from enum import Enum

from sqlalchemy import Column
from sqlalchemy.dialects.mysql import VARCHAR, TINYINT, DECIMAL

from application.model.base_model import Base, BaseModelMixin


class PayOrder(Base, BaseModelMixin):
    __tablename__ = 'pay_order'
    __comment__ = '付款订单'

    type = Column(TINYINT, nullable=False, comment='1 - 充值，2 - 消费，3 - 转账，4 - 提现')
    amount = Column(DECIMAL(12, 2), nullable=False, comment='支付金额')
    trade_order_uuid = Column(VARCHAR(36), nullable=False, comment='账户持有人UUID')
    payment_method_uuid = Column(VARCHAR(36), nullable=False, comment='支付渠道UUID')
    payment_method_token = Column(VARCHAR(64), comment='支付渠道唯一标识符')

    class Status(Enum):
        # 状态：0 - 初始化，1 - 支付完成，2 - 作废，3 - 支付中
        INITIALIZATION = 0
        FINISH = 1
        DELETED = 2

    class Type(Enum):
        RECHARGE = 1
        CONSUME = 2

    def __init__(self, order_type: int, amount, trade_order_uuid: str, payment_method_uuid: str,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.type = order_type
        self.amount = amount
        self.trade_order_uuid = trade_order_uuid
        self.payment_method_uuid = payment_method_uuid

        self.status = 0


cacheable = PayOrder
