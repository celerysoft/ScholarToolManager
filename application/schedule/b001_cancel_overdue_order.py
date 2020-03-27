# -*-coding:utf-8 -*-
"""
自动取消超时未支付的订单脚本
续费服务订单的超时时间：>7天
新建服务订单的超时时间：>30分钟
执行频率：每隔30分钟执行
执行优先级：B-1
"""
from datetime import datetime, timedelta

from application.model.service_trade_order import ServiceTradeOrder
from application.model.trade_order import TradeOrder
from application.util.database import session_scope


class CancelOverdueOrderScript:
    THRESHOLD_FOR_SUBSCRIBE_ORDER = timedelta(minutes=30)
    THRESHOLD_FOR_RENEW_ORDER = timedelta(days=7)

    def execute(self):
        now = datetime.now()
        with session_scope() as session:
            orders = session.query(TradeOrder) \
                .filter(TradeOrder.type == TradeOrder.TYPE.CONSUME.value,
                        TradeOrder.status == TradeOrder.STATUS.INITIALIZATION.value) \
                .all()
            for order in orders:  # type: TradeOrder
                relationship = session.query(ServiceTradeOrder) \
                    .filter(ServiceTradeOrder.trade_order_uuid == order.uuid,
                            ServiceTradeOrder.status == ServiceTradeOrder.STATUS.VALID.value) \
                    .first()  # type: ServiceTradeOrder
                if relationship is None:
                    self.cancel_subscribe_order(now, order)
                else:
                    self.cancel_renew_order(now, order)

    @classmethod
    def cancel_subscribe_order(cls, now: datetime, order: TradeOrder):
        deadline = now - cls.THRESHOLD_FOR_SUBSCRIBE_ORDER
        if order.created_at < deadline:
            order.status = TradeOrder.STATUS.CANCEL.value

    @classmethod
    def cancel_renew_order(cls, now: datetime, order: TradeOrder):
        deadline = now - cls.THRESHOLD_FOR_RENEW_ORDER
        if order.created_at < deadline:
            order.status = TradeOrder.STATUS.CANCEL.value


script = CancelOverdueOrderScript()


if __name__ == '__main__':
    # script = CancelOverdueOrderScript()
    # script.execute()
    raise RuntimeError('Do not execute this script directory, execute b000_execute_b_series_schedules.py instead')
