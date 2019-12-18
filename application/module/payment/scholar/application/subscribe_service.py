# -*-coding:utf-8 -*-
"""
学术积分账户支付系统 - 充值模块
"""
from datetime import datetime, timedelta

import configs
from application.model.pay_order import PayOrder
from application.model.scholar_payment_account import ScholarPaymentAccount
from application.model.scholar_payment_account_log import ScholarPaymentAccountLog
from application.model.service import Service
from application.model.subscribe_service_snapshot import SubscribeServiceSnapshot
from application.model.trade_order import TradeOrder
from application.module.payment.scholar.application.base import BaseComponent
from application.util import date_util, background_task
from application.util.database import session_scope


class SubScribeService(BaseComponent):
    def subscribe(self, payload: dict):
        try:
            app_id = payload['app_id']
            timestamp = payload['timestamp']
            trade_order_uuid = payload['trade_order_uuid']
            signature = payload['signature']
        except KeyError:
            raise RuntimeError('非法请求')

        expect_signature = self._derive_signature(timestamp, app_id, configs.SCHOLAR_PAYMENT_SYSTEM_APP_SECRET)
        if signature != expect_signature:
            raise RuntimeError('签名不合法')

        with session_scope() as session:
            trade_order = session.query(TradeOrder) \
                .filter(TradeOrder.uuid == trade_order_uuid).first()  # type: TradeOrder
            if trade_order.status not in [TradeOrder.STATUS.INITIALIZATION.value, TradeOrder.STATUS.PAYING.value]:
                raise RuntimeError('订单状态错误，无法支付')

            account = session.query(ScholarPaymentAccount) \
                .filter(ScholarPaymentAccount.user_uuid == trade_order.user_uuid,
                        ScholarPaymentAccount.status == ScholarPaymentAccount.STATUS.VALID.value) \
                .first()  # type: ScholarPaymentAccount

            pay_orders = session.query(PayOrder).filter(PayOrder.trade_order_uuid == trade_order_uuid,
                                                        PayOrder.status == PayOrder.Status.FINISH.value).all()
            amount = 0
            for order in pay_orders:  # type: PayOrder
                amount += order.amount
            else:
                amount = trade_order.amount

            old_balance = account.balance
            new_balance = old_balance - amount

            pay_order = self._create_pay_order(
                session=session,
                amount=amount,
                trade_order_uuid=trade_order.uuid,
            )  # type: PayOrder

            log = self.decrease(
                session=session,
                account_uuid=account.uuid,
                old_balance=old_balance,
                amount=amount,
                new_balance=new_balance,
                purpose_type=ScholarPaymentAccountLog.PurposeType.CONSUME
            )  # type: ScholarPaymentAccountLog
            if log is not None and log.status == ScholarPaymentAccountLog.Status.VALID.value:
                pay_order.payment_method_token = log.uuid
                pay_order.status = PayOrder.Status.FINISH.value
                account.balance = new_balance

            if pay_order.status == PayOrder.Status.FINISH.value and pay_order.amount == amount:
                trade_order.status = TradeOrder.STATUS.FINISH.value

            print('订单{}支付完毕，共支付{}学术积分'.format(trade_order_uuid, pay_order.amount))

            self._create_service(session, trade_order_uuid)
            return True

    @staticmethod
    def _create_pay_order(session, amount, trade_order_uuid):
        pay_order = PayOrder(
            order_type=PayOrder.Type.RECHARGE.value,
            amount=amount,
            trade_order_uuid=trade_order_uuid,
            payment_method_uuid=configs.SCHOLAR_PAYMENT_SYSTEM_UUID_IN_PAYMENT_METHOD,
        )
        session.add(pay_order)
        session.flush()
        return pay_order

    def _create_service(self, session, trade_order_uuid):
        snapshot = session.query(SubscribeServiceSnapshot) \
            .filter(SubscribeServiceSnapshot.trade_order_uuid == trade_order_uuid,
                    SubscribeServiceSnapshot.status == SubscribeServiceSnapshot.STATUS.ACTIVATED) \
            .first()  # type: SubscribeServiceSnapshot

        service_type = snapshot.type
        now = datetime.now()
        last_reset_at = None
        auto_renew = snapshot.auto_renew
        if service_type == Service.TYPE.MONTHLY:
            reset_at = date_util.derive_1st_datetime_of_next_month(now)
            if auto_renew:
                expired_at = datetime(2099, 12, 31, 23, 59, 59)
            else:
                expired_at = reset_at
        elif service_type == Service.TYPE.DATA:
            reset_at = None
            expired_at = now + timedelta(days=365)
        else:
            raise RuntimeError('未知的服务类型')

        port = self._derive_available_shadowsocks_port(session)
        service = Service(
            user_uuid=snapshot.user_uuid,
            template_uuid=snapshot.service_template_uuid,
            service_type=snapshot.type,
            package=snapshot.package,
            usage=0,
            auto_renew=snapshot.auto_renew,
            reset_at=reset_at,
            last_reset_at=last_reset_at,
            expired_at=expired_at,
            total_usage=0,
            port=port,
            password=snapshot.service_password)
        session.add(service)

        background_task.add_port.delay(port=port, password=snapshot.service_password)

    @staticmethod
    def _derive_available_shadowsocks_port(session) -> int:
        valid_status = [Service.STATUS.INITIALIZATION, Service.STATUS.ACTIVATED, Service.STATUS.SUSPENDED]
        service = session.query(Service) \
            .order_by(Service.port.desc()) \
            .filter(Service.status.in_(valid_status)) \
            .first()  # type: Service

        if service is None:
            return configs.SERVICE_MIN_PORT
        else:
            return service.port + 1


subscribe_service_module = SubScribeService()
