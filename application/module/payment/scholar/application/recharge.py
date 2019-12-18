# -*-coding:utf-8 -*-
"""
学术积分账户支付系统 - 充值模块
"""
from decimal import Decimal

import configs
from application.model.pay_order import PayOrder
from application.model.scholar_payment_account import ScholarPaymentAccount
from application.model.scholar_payment_account_log import ScholarPaymentAccountLog
from application.model.trade_order import TradeOrder
from application.module.payment.scholar.application.base import BaseComponent
from application.util.database import session_scope


class Recharge(BaseComponent):
    def recharge(self, payload: dict):
        try:
            app_id = payload['app_id']
            timestamp = payload['timestamp']
            user_uuid = payload['user_uuid']
            amount = payload['amount']
            signature = payload['signature']
        except KeyError:
            raise RuntimeError('非法请求')

        amount = Decimal(amount)

        expect_signature = self._derive_signature(timestamp, app_id, configs.SCHOLAR_PAYMENT_SYSTEM_APP_SECRET)
        if signature != expect_signature:
            raise RuntimeError('签名不合法')

        with session_scope() as session:
            account = session.query(ScholarPaymentAccount) \
                .filter(ScholarPaymentAccount.user_uuid == user_uuid,
                        ScholarPaymentAccount.status == ScholarPaymentAccount.STATUS.VALID.value) \
                .first()  # type: ScholarPaymentAccount

            old_balance = account.balance
            new_balance = old_balance + amount

            trade_order = self._create_trade_order(
                session=session,
                user_uuid=user_uuid,
                amount=amount
            )  # type: TradeOrder

            pay_order = self._create_pay_order(
                session=session,
                amount=trade_order.amount,
                trade_order_uuid=trade_order.uuid,
            )  # type: PayOrder

            log = self.increase(
                session=session,
                account_uuid=account.uuid,
                old_balance=old_balance,
                amount=amount,
                new_balance=new_balance,
                purpose_type=ScholarPaymentAccountLog.PurposeType.RECHARGE
            )  # type: ScholarPaymentAccountLog

            if log is not None:
                pay_order.payment_method_token = log.uuid
                pay_order.status = PayOrder.Status.FINISH.value

            if pay_order.status == PayOrder.Status.FINISH.value and trade_order.amount == pay_order.amount:
                trade_order.status = TradeOrder.STATUS.FINISH.value

            if trade_order.status == TradeOrder.STATUS.FINISH.value:
                account.balance = new_balance

            print('已收到为用户{}充值{}学术积分的请求'.format(user_uuid, amount))
            return True

    @staticmethod
    def _create_trade_order(session, user_uuid, amount):
        order = TradeOrder(
            user_uuid=user_uuid,
            order_type=TradeOrder.TYPE.RECHARGE.value,
            amount=amount,
            description='学术积分余额充值'
        )
        session.add(order)
        session.flush()
        return order

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


recharge = Recharge()
