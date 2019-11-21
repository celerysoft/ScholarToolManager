# -*- coding: utf-8 -*-
from flask import make_response

import configs
from application import exception
from application.model.model import User, UserScholarBalance, UserScholarBalanceLog
from application.util import permission
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


class ScholarBalanceAPI(BaseNeedLoginAPI):
    methods = ['GET', 'PATCH']
    need_login_methods = ['GET', 'PATCH']

    def get(self):
        """
        api_get_scholar_balance
        :return:
        """
        target_user_id = self.get_data('user_id')
        if self.valid_data(target_user_id):
            return self.get_scholar_balance(target_user_id)
        else:
            return self.get_self_scholar_balance()

    def get_scholar_balance(self, target_user_id):
        with session_scope() as session:
            if not permission.toolkit.check_manage_scholar_balance_permission(session, self.user_id):
                raise exception.api.Forbidden('当前用户无权管理学术积分')

            user_scholar_balance = session.query(UserScholarBalance) \
                .filter(UserScholarBalance.user_id == target_user_id).first()

            balance = user_scholar_balance.balance

        result = ApiResult('获取学术积分成功', payload={
            'user_id': target_user_id,
            'balance': balance
        })
        return make_response(result.to_response())

    def get_self_scholar_balance(self):
        target_user_id = self.user_id

        with session_scope() as session:

            user_scholar_balance = session.query(UserScholarBalance) \
                .filter(UserScholarBalance.user_id == target_user_id).first()

            balance = user_scholar_balance.balance

        result = ApiResult('获取学术积分成功', payload={
            'user_id': target_user_id,
            'balance': balance
        })
        return make_response(result.to_response())

    def patch(self):
        """
        api_update_scholar_balance
        :return:
        """
        target_user_id = self.get_post_data('user_id', require=True, error_message='缺少user_id字段')
        amount = self.get_post_data('amount', require=True, error_message='缺少amount字段')
        try:
            amount = int(amount)
            if amount <= 0:
                raise exception.api.InvalidRequest('金额必须大于0')
        except BaseException as e:
            raise exception.api.InvalidRequest('请输入合法的金额：{}'.format(e))

        with session_scope() as session:
            if not permission.toolkit.check_manage_scholar_balance_permission(session, self.user_id):
                raise exception.api.Forbidden('当前用户无权管理学术积分')

            user_scholar_balance = session.query(UserScholarBalance) \
                .filter(UserScholarBalance.user_id == target_user_id).first()

            user_scholar_balance.balance += amount

            user_scholar_balance_log = UserScholarBalanceLog(
                user_id=target_user_id,
                amount=amount,
                balance=user_scholar_balance.balance,
                message='系统发放'
            )
            session.add(user_scholar_balance_log)

        result = ApiResult('充值学术积分成功', 201)
        return make_response(result.to_response())


view = ScholarBalanceAPI
