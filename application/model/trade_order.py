# -*- coding: utf-8 -*-
from enum import Enum

from sqlalchemy import Column
from sqlalchemy.dialects.mysql import VARCHAR, TINYINT, TEXT, DECIMAL

from application.model.base_model import Base, BaseModelMixin


class TradeOrder(Base, BaseModelMixin):
    __tablename__ = 'trade_order'
    __comment__ = '交易订单'

    user_uuid = Column(VARCHAR(36), nullable=False, comment='账户持有人UUID')
    type = Column(TINYINT, nullable=False, comment='0 - 退款，1 - 充值，2 - 消费，3 - 转账，4 - 提现')
    amount = Column(DECIMAL(12, 2), nullable=False, comment='交易金额')
    description = Column(TEXT, comment='订单描述')

    class STATUS(Enum):
        # 状态：0 - 初始化，1 - 支付完成，2 - 作废，3 - 支付中，4 - 部分支付，5 - 退款中，6 - 部分退款，7 - 全部退款，8 - 取消
        INITIALIZATION = 0
        FINISH = 1
        DELETED = 2
        PAYING = 3
        PARTIAL_PAY = 4
        CANCEL = 8

    class TYPE(Enum):
        RECHARGE = 1
        CONSUME = 2

    def __init__(self, user_uuid: str, order_type: int, amount, description: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user_uuid = user_uuid
        self.type = order_type
        self.amount = amount
        self.description = description

        self.status = 0


cacheable = TradeOrder
