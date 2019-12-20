# -*- coding: utf-8 -*-
from decimal import Decimal

from application import exception
from application.model.scholar_payment_account import ScholarPaymentAccount
from application.util import scholar_payment_system
from application.util.database import session_scope
from application.views.base_api import PermissionRequiredAPI, ApiResult


class ManagementScholarPaymentAccountAPI(PermissionRequiredAPI):
    methods = ['GET', 'PATCH']

    def get(self):
        user_uuid = self.get_data('user_uuid')
        if self.valid_data(user_uuid):
            return self.get_single_account(user_uuid)

        with session_scope() as session:
            account_list = []
            query = self.derive_query_for_get_method(session, ScholarPaymentAccount) \
                .filter(ScholarPaymentAccount.status != ScholarPaymentAccount.STATUS.DELETED.value)
            page, page_size, offset, max_page = self.derive_page_parameter(query.count())
            accounts = query.offset(offset).limit(page_size).all()
            for account in accounts:  # type: ScholarPaymentAccount
                account_list.append(account.to_dict())

            result = ApiResult('获取学术积分账户信息成功', payload={
                'accounts': account_list,
                'page': page,
                'page_size': page_size,
                'max_page': max_page,
            })
            return result.to_response()

    def get_single_account(self, user_uuid):
        with session_scope() as session:
            account = session.query(ScholarPaymentAccount) \
                .filter(ScholarPaymentAccount.user_uuid == user_uuid,
                        ScholarPaymentAccount.status != ScholarPaymentAccount.STATUS.DELETED.value) \
                .first()  # type: ScholarPaymentAccount

            if account is None:
                raise exception.api.NotFound('学术积分账户不存在')

            result = ApiResult('获取学术积分账户信息成功', payload={
                'account': account.to_dict()
            })
            return result.to_response()

    def patch(self):
        target_user_uuid = self.get_post_data('user_uuid', require=True, error_message='缺少user_uuid字段')
        amount = self.get_post_data('amount', require=True, error_message='缺少amount字段')
        try:
            amount = Decimal(amount)
            if amount <= 0:
                raise exception.api.InvalidRequest('充值金额必须大于0')
        except BaseException as e:
            raise exception.api.InvalidRequest('请输入合法的金额：{}'.format(e))

        scholar_payment_system.toolkit.recharge(target_user_uuid, amount)

        result = ApiResult('学术积分充值的请求已收到，正在后台充值', 200)
        return result.to_response()


view = ManagementScholarPaymentAccountAPI
