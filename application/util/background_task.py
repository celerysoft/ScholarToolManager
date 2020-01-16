# -*-coding:utf-8 -*-
"""
基于Celery实现的后台消息队列
"""
from celery import Celery

import configs
from application.util import shadowsocks_controller, email

celery_app = Celery('app',
                    broker=configs.CELERY_BROKER_URL,
                    backend=configs.CELERY_RESULT_BACKEND)


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


@celery_app.task
def send_activation_email(user_email, username, activate_url):
    email.toolkit.send_activation_email(user_email, username, activate_url)


@celery_app.task
def send_activation_email_for_modifying_email_address(user_email, username, activate_url):
    email.toolkit.send_activation_email_for_modifying_email_address(user_email, username, activate_url)


@celery_app.task
def send_reset_password_email(user_email, username, reset_password_url):
    email.toolkit.send_reset_password_email(user_email, username, reset_password_url)
