# -*-coding:utf-8 -*-
"""
celery -A app worker --loglevel=info
"""
from celery import Celery

import configs
from application.module.payment.scholar.application.recharge import recharge as recharge_module

app = Celery('scholar_payment_system_app',
             broker=configs.CELERY_BROKER_URL,
             backend=configs.CELERY_RESULT_BACKEND)


@app.task
def recharge(payload):
    recharge_module.recharge(payload)
