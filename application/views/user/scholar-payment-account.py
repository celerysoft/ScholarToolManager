# -*- coding: utf-8 -*-
from decimal import Decimal

from application import exception
from application.model.scholar_payment_account import ScholarPaymentAccount
from application.util import scholar_payment_system
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


class ScholarPaymentAccountAPI(BaseNeedLoginAPI):
    methods = ['GET']

    def get(self):
        with session_scope() as session:
            account = session.query(ScholarPaymentAccount) \
                .filter(ScholarPaymentAccount.user_uuid == self.user_uuid,
                        ScholarPaymentAccount.status == ScholarPaymentAccount.STATUS.VALID.value) \
                .first()  # type: ScholarPaymentAccount

            if account is None:
                raise exception.api.NotFound('学术积分账户不存在')

            result = ApiResult('获取学术积分账户信息成功', payload={
                'account': account.to_dict()
            })
            return result.to_response()


view = ScholarPaymentAccountAPI
