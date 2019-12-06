# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import TINYINT, BIGINT, VARCHAR, TEXT, INTEGER

from application.model.base_model import Base, BaseModelMixin


class SubscribeServiceSnapshot(Base, BaseModelMixin):
    __tablename__ = 'subscribe_service_snapshot'
    __comment__ = '订购学术服务交易快照'

    trade_order_uuid = Column(VARCHAR(36), nullable=False, comment='交易订单UUID')
    service_template_uuid = Column(VARCHAR(36), nullable=False, comment='学术服务模板UUID')

    type = Column(TINYINT, nullable=False, comment='0 - 包月套餐，1 - 流量套餐')
    title = Column(VARCHAR(64), nullable=False, comment='套餐名')
    subtitle = Column(VARCHAR(64), nullable=False, comment='副标题')
    description = Column(TEXT, nullable=False, comment='套餐描述')
    package = Column(BIGINT, nullable=False, comment='总流量')
    price = Column(INTEGER, nullable=False, comment='价格')
    initialization_fee = Column(INTEGER, nullable=False, comment='初装费')

    class STATUS(object):
        # 初始化
        INACTIVATED = 0
        # 有效
        ACTIVATED = 1
        # 已删除
        DELETED = 2

    class TYPE(object):
        # 包月
        MONTHLY = 0
        # 流量
        DATA = 1

    def __init__(self, trade_order_uuid: str, service_template_uuid: str, service_type: int, title: str, subtitle: str,
                 description: str, package: int, price: int, initialization_fee: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.trade_order_uuid = trade_order_uuid
        self.service_template_uuid = service_template_uuid
        self.type = service_type
        self.title = title
        self.subtitle = subtitle
        self.description = description
        self.package = package
        self.price = price
        self.initialization_fee = initialization_fee
        self.status = 1


cacheable = SubscribeServiceSnapshot
