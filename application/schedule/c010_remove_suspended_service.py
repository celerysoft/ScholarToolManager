# -*-coding:utf-8 -*-
"""
将已欠费的学术服务标记为已失效
执行频率：每天执行
执行优先级：C-10
"""
from datetime import date, timedelta

from application.model.service import Service
from application.model.service_trade_order import ServiceTradeOrder
from application.model.trade_order import TradeOrder
from application.util.database import session_scope


class RemoveSuspendedServiceScript:
    THRESHOLD = timedelta(days=7)

    def execute(self):
        today = date.today()
        deadline = today - self.THRESHOLD
        with session_scope() as session:
            while True:
                services = session.query(Service) \
                    .filter(Service.status == Service.STATUS.SUSPENDED,
                            Service.billing_date <= deadline) \
                    .limit(500).all()

                if services is None or len(services) == 0:
                    break

                for service in services:  # type: Service
                    service.status = Service.STATUS.INVALID

                    # TODO 对交易订单进行退款，而不是暴力关闭
                    trade_orders = session.query(TradeOrder) \
                        .filter(ServiceTradeOrder.service_uuid == service.uuid,
                                ServiceTradeOrder.status == ServiceTradeOrder.STATUS.VALID.value,
                                TradeOrder.uuid == ServiceTradeOrder.trade_order_uuid,
                                TradeOrder.status.in_([TradeOrder.STATUS.INITIALIZATION.value,
                                                       TradeOrder.STATUS.PAYING.value,
                                                       TradeOrder.STATUS.PARTIAL_PAY.value])) \
                        .all()
                    for trade_order in trade_orders:  # type: TradeOrder
                        trade_order.status = TradeOrder.STATUS.CANCEL.value

                    session.commit()


script = RemoveSuspendedServiceScript()


if __name__ == '__main__':
    # script = RemoveSuspendedServiceScript()
    # script.execute()
    raise RuntimeError('Do not execute this script directory, execute c000_execute_c_series_schedules.py instead')
