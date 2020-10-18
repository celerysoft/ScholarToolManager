# -*-coding:utf-8 -*-
"""
执行A系列定时任务
执行频率：每天执行
"""
from datetime import datetime

from application.schedule.a001_create_order_for_expired_service import CreateOrderForExpiredServiceScript
from application.schedule.a005_pay_order_for_auto_renew_service import PayOrderForAutoRenewServiceScript

if __name__ == '__main__':
    now = datetime.now()

    a001_script = CreateOrderForExpiredServiceScript()
    a001_script.execute()

    if now.day == 1:
        a005_script = PayOrderForAutoRenewServiceScript()
        a005_script.execute()
