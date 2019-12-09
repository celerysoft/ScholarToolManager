# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import TINYINT, BIGINT, DATETIME, VARCHAR, INTEGER

from application.model.base_model import Base, BaseModelMixin


class Service(Base, BaseModelMixin):
    __tablename__ = 'service'
    __comment__ = '学术服务'

    user_uuid = Column(VARCHAR(36), nullable=False, comment='所属用户uuid')
    template_uuid = Column(VARCHAR(36), nullable=False, comment='学术服务模板uuid')
    type = Column(TINYINT, nullable=False, comment='0 - 包月套餐，1 - 流量套餐')
    usage = Column(BIGINT, nullable=False, comment='已用流量')
    package = Column(BIGINT, nullable=False, comment='总流量')
    auto_renew = Column(TINYINT, comment='自动续费状态：0 - 不自动，1 - 自动续费，包月套餐专用字段')
    reset_at = Column(DATETIME, comment='下次将已用流量重置为0的时间点，包月套餐专用字段')
    last_reset_at = Column(DATETIME, comment='上次将已用流量重置为0的时间点，暨上次续费的时间')
    expired_at = Column(DATETIME, comment='套餐过期时间，流量套餐专用字段')
    total_usage = Column(BIGINT, nullable=False, comment='已使用流量合计')
    port = Column(INTEGER, nullable=False, comment='服务绑定的端口号')
    password = Column(VARCHAR(64), nullable=False, comment='服务密码')

    class STATUS(object):
        # 初始化，待创建订单
        INITIALIZATION = 0
        # 有效
        ACTIVATED = 1
        # 已删除
        DELETED = 2
        # 已暂停，待续费
        SUSPENDED = 3
        # 已失效
        INVALID = 4
        # 订单创建成功，待支付
        CREATED = 5

    class TYPE(object):
        # 包月
        MONTHLY = 0
        # 流量
        DATA = 1

    def __init__(self, user_uuid, template_uuid, service_type, package, usage, auto_renew, reset_at,
                 last_reset_at, expired_at, total_usage, port: int, password: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user_uuid = user_uuid
        self.template_uuid = template_uuid
        self.type = service_type
        self.usage = usage
        self.package = package
        self.auto_renew = auto_renew
        self.reset_at = reset_at
        self.last_reset_at = last_reset_at
        self.expired_at = expired_at
        self.total_usage = total_usage
        self.port = port
        self.password = password

        self.status = 1


cacheable = Service
