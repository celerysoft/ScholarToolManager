# -*-coding:utf-8 -*-
"""
基于Celery实现的后台消息队列
"""
from celery import Celery

import configs
from util import shadowsocks_controller

celery_app = Celery('app',
                    broker=configs.Config.CELERY_BROKER_URL,
                    backend=configs.Config.CELERY_RESULT_BACKEND)


@celery_app.task
def add_port(port, password):
    shadowsocks_controller.add_port(port, password)


@celery_app.task
def remove_port(port):
    shadowsocks_controller.remove_port(port)


@celery_app.task
def modify_port_password(port, password):
    shadowsocks_controller.remove_port(port)
    shadowsocks_controller.add_port(port, password)
