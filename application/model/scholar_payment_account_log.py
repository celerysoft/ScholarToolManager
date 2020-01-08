# -*- coding: utf-8 -*-
from enum import Enum

from sqlalchemy import Column
from sqlalchemy.dialects.mysql import VARCHAR, DECIMAL, TINYINT

from application.model.base_model import Base, BaseModelMixin


class ScholarPaymentAccountLog(Base, BaseModelMixin):
    __tablename__ = 'scholar_payment_account_log'
    __comment__ = '学术积分账户流水'

    account_uuid = Column(VARCHAR(36), nullable=False, comment='学术积分账户UUID')
    pay_order_uuid = Column(VARCHAR(36), nullable=False, comment='流水对应的支付订单UUID')
    former_balance = Column(DECIMAL(12, 2), nullable=False, comment='账户余额')
    amount = Column(DECIMAL(12, 2), nullable=False, comment='金额')
    balance = Column(DECIMAL(12, 2), nullable=False, comment='账户余额')
    type = Column(TINYINT, nullable=False, comment='0 - 减少，1 - 增加')
    purpose_type = Column(TINYINT, nullable=False,
                          comment='0 - 消费(-)，1 - 充值(+)，2 - 转出(-)，3 - 转入(+)，4 - 补缴(-)，5 - 补偿(+)')

    class Type(Enum):
        DECREASE = 0
        INCREASE = 1

    class PurposeType(Enum):
        CONSUME = 0
        RECHARGE = 1

    class Status(Enum):
        INITIALIZATION = 0
        VALID = 1
        DELETED = 2

    def __init__(self, account_uuid: str, pay_order_uuid: str, former_balance, amount, balance,
                 log_type, purpose_type, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.account_uuid = account_uuid
        self.pay_order_uuid = pay_order_uuid
        self.former_balance = former_balance
        self.balance = balance
        self.amount = amount
        self.type = log_type
        self.purpose_type = purpose_type
        self.status = 1


cacheable = ScholarPaymentAccountLog
