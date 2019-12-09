# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import TINYINT, BIGINT, VARCHAR, TEXT, DECIMAL

from application.model.base_model import Base, BaseModelMixin


class ServiceTemplate(Base, BaseModelMixin):
    __tablename__ = 'service_template'
    __comment__ = '学术服务'

    type = Column(TINYINT, nullable=False, comment='0 - 包月套餐，1 - 流量套餐')
    title = Column(VARCHAR(64), nullable=False, comment='套餐名')
    subtitle = Column(VARCHAR(64), nullable=False, comment='副标题')
    description = Column(TEXT, nullable=False, comment='套餐描述')
    package = Column(BIGINT, nullable=False, comment='总流量')
    price = Column(DECIMAL(12, 2), nullable=False, comment='价格')
    initialization_fee = Column(DECIMAL(12, 2), nullable=False, comment='初装费')

    class STATUS(object):
        # 初始化
        INITIALIZATION = 0
        # 有效
        VALID = 1
        # 已删除
        DELETED = 2
        # 下架
        SUSPEND = 3

    class TYPE(object):
        # 包月
        MONTHLY = 0
        # 流量
        DATA = 1
        # 推荐
        RECOMMENDATION = 2

    def __init__(self, service_type: int, title: str, subtitle: str, description: str, package: int, price,
                 initialization_fee, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.type = service_type
        self.title = title
        self.subtitle = subtitle
        self.description = description
        self.package = package
        self.price = price
        self.initialization_fee = initialization_fee
        self.status = 1


cacheable = ServiceTemplate
