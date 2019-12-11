# -*- coding: utf-8 -*-
from application import exception
from application.model.payment_method import PaymentMethod
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


class PaymentMethodAPI(BaseNeedLoginAPI):
    methods = ['GET']

    def get(self):
        with session_scope() as session:
            payment_methods = session.query(PaymentMethod) \
                .filter(PaymentMethod.status != PaymentMethod.STATUS.DELETED.value) \
                .order_by(PaymentMethod.id) \
                .all()
            if len(payment_methods) == 0:
                raise exception.api.NotFound('暂无有效的支付方式')

            payment_method_list = []
            for payment_method in payment_methods:  # type: PaymentMethod
                payment_method_list.append(payment_method.to_dict())

            result = ApiResult('获取支付方式信息成功', payload={
                'payment_methods': payment_method_list,
            })
            return result.to_response()


view = PaymentMethodAPI
