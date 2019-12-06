# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import VARCHAR, TINYINT, DECIMAL

from application.model.base_model import Base, BaseModelMixin


class RefundOrder(Base, BaseModelMixin):
    __tablename__ = 'refund_order'
    __comment__ = '退款订单'

    type = Column(TINYINT, nullable=False, comment='1 - 充值，2 - 消费，3 - 转账，4 - 提现')
    amount = Column(DECIMAL(12, 2), nullable=False, comment='退款金额')
    trade_order_uuid = Column(VARCHAR(36), nullable=False, comment='账户持有人UUID')
    payment_method_uuid = Column(VARCHAR(36), nullable=False, comment='支付渠道UUID')
    payment_method_token = Column(VARCHAR(64), nullable=False, comment='支付渠道唯一标识符')

    class STATUS(object):
        # 状态：0 - 初始化，1 - 退款完成，2 - 作废，3 - 退款中
        INITIALIZATION = 0
        VALID = 1
        DELETED = 2

    def __init__(self, order_type: int, amount, trade_order_uuid: str, payment_method_uuid: str,
                 payment_method_token: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.type = order_type
        self.amount = amount
        self.trade_order_uuid = trade_order_uuid
        self.payment_method_uuid = payment_method_uuid
        self.payment_method_token = payment_method_token

        self.status = 0


cacheable = RefundOrder
