# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import TINYINT, BIGINT, DATE, VARCHAR, INTEGER

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
    billing_date = Column(DATE, nullable=False, comment='账单日，下次付款的时间')
    total_usage = Column(BIGINT, nullable=False, comment='已使用流量合计')
    port = Column(INTEGER, nullable=False, comment='服务绑定的端口号')
    password = Column(VARCHAR(64), nullable=False, comment='服务密码')

    class STATUS(object):
        """
        学术服务状态流程：
                                     -- 到期 --> 欠费(5) -- 欠费超过3天 --> 暂停(3) -------------
        包月服务：初始化(0) -> 有效(1) -|                                                      |-- 到期不续费到达7天 --> 失效(4)
                                    -- 流量超出 --> 欠费(5) -- 流量超出10% --> 暂停(3) -- 到期 --

                                     -- 到期 --> 欠费(5) -- 欠费超过3天 --> 暂停(3) -------------
        流量服务：初始化(0) -> 有效(1) -|                                                      |-- 到期不续费到达7天 --> 失效(4)
                                    -- 流量超出 --> 欠费(5) -- 流量超出10% --> 暂停(3) -- 到期 --
        """
        # 初始化（无法使用，无法续费）
        INITIALIZATION = 0
        # 有效（可以使用，无法续费）
        ACTIVATED = 1
        # 已删除（无法使用，无法续费）
        DELETED = 2
        # 已暂停，待续费（无法使用，可以续费）
        SUSPENDED = 3
        # 已失效（无法使用，无法续费）
        INVALID = 4
        # 欠费（可以使用，可以续费）
        OUT_OF_CREDIT = 5

    class TYPE(object):
        # 包月
        MONTHLY = 0
        # 流量
        DATA = 1

    def __init__(self, user_uuid, template_uuid, service_type, package, usage, auto_renew, billing_date,
                 total_usage, port: int, password: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user_uuid = user_uuid
        self.template_uuid = template_uuid
        self.type = service_type
        self.usage = usage
        self.package = package
        self.auto_renew = auto_renew
        self.billing_date = billing_date
        self.total_usage = total_usage
        self.port = port
        self.password = password

        self.status = 1


cacheable = Service
