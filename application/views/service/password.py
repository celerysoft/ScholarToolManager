# -*- coding: utf-8 -*-
from application import exception
from application.model.service import Service
from application.util import background_task
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


class ServicePasswordAPI(BaseNeedLoginAPI):
    methods = ['PUT']

    def put(self):
        service_uuid = self.get_post_data('uuid', require=True, error_message='缺少uuid字段')
        password = self.get_post_data('password', require=True, error_message='请输入长度至少为1位的新密码')

        with session_scope() as session:
            service = session.query(Service).filter(Service.uuid == service_uuid).first()
            if service is None:
                raise exception.api.NotFound('套餐不存在')

            if service.user_uuid != self.user_uuid:
                raise exception.api.Forbidden('无权修改其他用户的学术服务密码')

            service.password = password

            if service.status == Service.STATUS.ACTIVATED:
                background_task.modify_port_password.delay(port=service.port, password=password)

            result = ApiResult('修改连接密码成功', 201)
            return result.to_response()


view = ServicePasswordAPI
