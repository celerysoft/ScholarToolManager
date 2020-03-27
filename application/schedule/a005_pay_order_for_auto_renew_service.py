# -*-coding:utf-8 -*-
"""
为自动续费的包月学术服务进行订单支付的脚本
执行频率：每月1号执行
执行优先级：A-5
"""
from datetime import datetime, timedelta

from application.model.service import Service
from application.model.service_trade_order import ServiceTradeOrder
from application.model.trade_order import TradeOrder
from application.util import scholar_payment_system
from application.util.database import session_scope


class PayOrderForAutoRenewServiceScript:
    def execute(self):
        now = datetime.now()
        if now.day == 1:
            self.pay_order_by_scholar_payment_system(now)

    @staticmethod
    def pay_order_by_scholar_payment_system(now: datetime):
        with session_scope() as session:
            deadline = now - timedelta(hours=1)
            orders = session.query(TradeOrder) \
                .filter(TradeOrder.type == TradeOrder.TYPE.CONSUME.value,
                        TradeOrder.status == TradeOrder.STATUS.INITIALIZATION.value,
                        TradeOrder.created_at > deadline) \
                .all()
            for order in orders:  # type: TradeOrder
                relationship = session.query(ServiceTradeOrder) \
                    .filter(ServiceTradeOrder.trade_order_uuid == order.uuid,
                            ServiceTradeOrder.status == ServiceTradeOrder.STATUS.VALID.value) \
                    .first()  # type: ServiceTradeOrder
                if relationship is None:
                    continue
                related_service = session.query(Service) \
                    .filter(Service.uuid == relationship.service_uuid,
                            Service.status.in_([Service.STATUS.INITIALIZATION, Service.STATUS.ACTIVATED,
                                                Service.STATUS.SUSPENDED])) \
                    .first()  # type: Service
                if related_service.auto_renew == 1:
                    scholar_payment_system.toolkit.pay_order(order.uuid)


script = PayOrderForAutoRenewServiceScript()


if __name__ == '__main__':
    # script = PayOrderForAutoRenewServiceScript()
    # script.execute()
    raise RuntimeError('Do not execute this script directory, execute a000_execute_a_series_schedules.py instead')
