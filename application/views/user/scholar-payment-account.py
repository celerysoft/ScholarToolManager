# -*- coding: utf-8 -*-
from application import exception
from application.model.scholar_payment_account import ScholarPaymentAccount
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


class ScholarBalanceAPI(BaseNeedLoginAPI):
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

    # def patch(self):
    #     """
    #     api_update_scholar_balance
    #     :return:
    #     """
    #     target_user_id = self.get_post_data('user_id', require=True, error_message='缺少user_id字段')
    #     amount = self.get_post_data('amount', require=True, error_message='缺少amount字段')
    #     try:
    #         amount = int(amount)
    #         if amount <= 0:
    #             raise exception.api.InvalidRequest('金额必须大于0')
    #     except BaseException as e:
    #         raise exception.api.InvalidRequest('请输入合法的金额：{}'.format(e))
    #
    #     with session_scope() as session:
    #         if not permission.toolkit.check_manage_scholar_balance_permission(session, self.user_id):
    #             raise exception.api.Forbidden('当前用户无权管理学术积分')
    #
    #         user_scholar_balance = session.query(UserScholarBalance) \
    #             .filter(UserScholarBalance.user_id == target_user_id).first()
    #
    #         user_scholar_balance.balance += amount
    #
    #         user_scholar_balance_log = UserScholarBalanceLog(
    #             user_id=target_user_id,
    #             amount=amount,
    #             balance=user_scholar_balance.balance,
    #             message='系统发放'
    #         )
    #         session.add(user_scholar_balance_log)
    #
    #     result = ApiResult('充值学术积分成功', 201)
    #     return make_response(result.to_response())


view = ScholarBalanceAPI
