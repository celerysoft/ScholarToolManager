# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from application.model.service_trade_order import ServiceTradeOrder
from application.model.subscribe_service_snapshot import SubscribeServiceSnapshot
from application.model.trade_order import TradeOrder


class TradeOrderToolkit:
    @classmethod
    def check_is_order_conflict(cls, session, user_uuid: str, service_template_uuid: str = None,
                                service_uuid: str = None):
        threshold_in_day = 1
        critical_time = datetime.now() - timedelta(days=threshold_in_day)

        # 根据service_uuid查找订单
        if service_uuid is not None:
            order = session.query(TradeOrder) \
                .filter(service_uuid == ServiceTradeOrder.service_uuid,
                        ServiceTradeOrder.trade_order_uuid == TradeOrder.uuid,
                        TradeOrder.status.in_([TradeOrder.STATUS.INITIALIZATION.value, TradeOrder.STATUS.PAYING.value]),
                        TradeOrder.created_at > critical_time).first()  # type: TradeOrder
            if order is not None:
                snapshot = session.query(SubscribeServiceSnapshot) \
                    .filter(SubscribeServiceSnapshot.trade_order_uuid == order.uuid,
                            SubscribeServiceSnapshot.status != SubscribeServiceSnapshot.STATUS.DELETED) \
                    .first()  # type: SubscribeServiceSnapshot
                return True, snapshot
            return False, None

        # 根据service_template_uuid查找订单
        if service_template_uuid is not None:
            orders = session.query(TradeOrder) \
                .filter(TradeOrder.user_uuid == user_uuid,
                        TradeOrder.status.in_([TradeOrder.STATUS.INITIALIZATION.value, TradeOrder.STATUS.PAYING.value]),
                        TradeOrder.created_at > critical_time).all()
            for order in orders:  # type: TradeOrder
                snapshot = session.query(SubscribeServiceSnapshot) \
                    .filter(SubscribeServiceSnapshot.trade_order_uuid == order.uuid,
                            SubscribeServiceSnapshot.status != SubscribeServiceSnapshot.STATUS.DELETED) \
                    .first()  # type: SubscribeServiceSnapshot
                if snapshot.service_template_uuid == service_template_uuid:
                    return True, snapshot
        return False, None


toolkit = TradeOrderToolkit()
