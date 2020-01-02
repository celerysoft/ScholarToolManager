# -*- coding: utf-8 -*-
from typing import Union

from application import exception
from application.model.service_template import ServiceTemplate
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


class ServiceTemplateAPI(BaseNeedLoginAPI):
    methods = ['GET']

    def get(self):
        template_uuid = self.get_data('uuid')
        if self.valid_data(template_uuid):
            return self.get_template_by_uuid(template_uuid)

        template_type = self.get_data('type')
        if self.valid_data(template_type):
            return self.get_template_by_type(template_type)

        return self.get_templates()

    def get_template_by_uuid(self, uuid: str):
        with session_scope() as session:
            service_template = session.query(ServiceTemplate) \
                .filter(ServiceTemplate.uuid == uuid).first()  # type: ServiceTemplate

            if service_template is None:
                raise exception.api.NotFound('服务模版不存在')

            result = ApiResult('获取服务模板信息成功', payload={
                'template': service_template.to_dict()
            })
            return result.to_response()

    def get_template_by_type(self, template_type: Union[str, int]):
        try:
            template_type = int(template_type)
        except ValueError:
            return exception.api.InvalidRequest('请输入正确的服务类型')

        if template_type == ServiceTemplate.TYPE.RECOMMENDATION:
            return self.get_recommendation_template()

        with session_scope() as session:
            query = session.query(ServiceTemplate).filter(ServiceTemplate.type == template_type,
                                                          ServiceTemplate.status == ServiceTemplate.STATUS.VALID)
            page, page_size, offset, max_page = self.derive_page_parameter(query.count())

            templates = query.offset(offset).limit(page_size).all()

            result = ApiResult('获取服务模板信息成功', 200, {
                'templates': self.models_to_list(templates),
                'page': page,
                'page_size': page_size,
                'max_page': max_page,
            })
            return result.to_response()

    def get_recommendation_template(self):
        size = self.get_data('size')
        try:
            size = int(size)
        except ValueError:
            size = 3

        with session_scope() as session:
            monthly_templates = session.query(ServiceTemplate) \
                .filter(ServiceTemplate.type == ServiceTemplate.TYPE.MONTHLY,
                        ServiceTemplate.status == ServiceTemplate.STATUS.VALID) \
                .order_by(ServiceTemplate.created_at.desc()).limit(size).all()

            data_templates = session.query(ServiceTemplate) \
                .filter(ServiceTemplate.type == ServiceTemplate.TYPE.DATA,
                        ServiceTemplate.status == ServiceTemplate.STATUS.VALID) \
                .order_by(ServiceTemplate.created_at.desc()).limit(size).all()

            result = ApiResult('获取服务模板信息成功', 200, {
                'monthly_services': self.models_to_list(monthly_templates),
                'data_services': self.models_to_list(data_templates),
            })
            return result.to_response()


view = ServiceTemplateAPI
