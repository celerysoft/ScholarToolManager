# -*- coding: utf-8 -*-
from flask import make_response

from application import exception
from application.model.legacy.model import ServicePassword, \
    UserService, Service
from application.util import background_task
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


class ServicePasswordAPI(BaseNeedLoginAPI):
    methods = ['PATCH']

    def patch(self):
        service_id = self.get_post_data('service_id', require=True, error_message='缺少service_id字段')
        new_password = self.get_post_data('new_password', require=True, error_message='请输入长度至少为1位的新密码')

        with session_scope() as session:
            service = session.query(Service).filter(Service.id == service_id).first()
            if service is None:
                raise exception.api.NotFound('套餐不存在')

            service_password = session.query(ServicePassword) \
                .filter(ServicePassword.service_id == service_id) \
                .filter(UserService.service_id == ServicePassword.service_id) \
                .filter(UserService.user_id == self.user_id).first()
            if service_password is None:
                raise exception.api.Forbidden('无权修改他人套餐的连接密码')

            service_password.password = new_password

            if service.available:
                background_task.modify_port_password.delay(port=service_password.port, password=new_password)

        result = ApiResult('修改连接密码成功', 201)
        return make_response(result.to_response())


view = ServicePasswordAPI
