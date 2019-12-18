# -*-coding:utf-8 -*-
"""
/Users/admin/Developer/Python/scholar-tool-manager
celery -A app worker --loglevel=info
"""
from celery import Celery

import configs
from application.module.payment.scholar.application.recharge import recharge as recharge_module
from application.module.payment.scholar.application.subscribe_service import subscribe_service_module

app = Celery('scholar_payment_system_app',
             broker=configs.SCHOLAR_PAYMENT_SYSTEM_CELERY_BROKER_URL,
             backend=configs.SCHOLAR_PAYMENT_SYSTEM_CELERY_RESULT_BACKEND)


@app.task
def recharge(payload):
    recharge_module.recharge(payload)


@app.task
def subscribe_service(payload):
    subscribe_service_module.subscribe(payload)
