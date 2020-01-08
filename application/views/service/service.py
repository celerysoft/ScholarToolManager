# -*- coding: utf-8 -*-
from flask import make_response, Blueprint

from app import derive_import_root, add_url_rules_for_blueprint
from application import exception
from application.model.service import Service
from application.model.service_template import ServiceTemplate
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


class ServiceAPI(BaseNeedLoginAPI):
    methods = ['GET', 'PATCH']

    def get(self):
        service_uuid = self.get_data('uuid')
        if self.valid_data(service_uuid):
            return self.get_service_by_uuid(service_uuid)
        else:
            return self.get_user_services(self.user_uuid)

    def get_user_services(self, user_uuid):
        with session_scope() as db_session:
            query = db_session.query(Service, ServiceTemplate.title) \
                .outerjoin(ServiceTemplate, Service.template_uuid == ServiceTemplate.uuid) \
                .filter(Service.user_uuid == user_uuid) \
                .filter(Service.status != Service.STATUS.DELETED) \
                .order_by(Service.created_at)

            page, page_size, offset, max_page = self._derive_page_parameter(query.count())

            services = query.offset(offset).limit(page_size).all()

            service_list = []
            for record in services:
                print(dir(record.Service))
                print(type(record.Service.billing_date), 123)
                service = record.Service
                service_dict = service.to_dict()
                service_dict['title'] = record.title
                service_list.append(service_dict)

            result = ApiResult('获取用户学术服务信息成功', payload={
                'page': page,
                'page_size': page_size,
                'max_page': max_page,
                'services': service_list
            })
            return result.to_response()

    def get_service_by_uuid(self, service_uuid):
        with session_scope() as session:
            service = session.query(Service).filter(Service.uuid == service_uuid,
                                                    Service.status != Service.STATUS.DELETED).first()
            if service is None:
                raise exception.api.NotFound('套餐不存在')

            if service.user_uuid != self.user_uuid:
                raise exception.api.Forbidden('无权查看其他用户的套餐信息')

            template = session.query(ServiceTemplate) \
                .filter(ServiceTemplate.uuid == service.template_uuid).first()
            service_dict = service.to_dict()
            service_dict['title'] = template.title
            service_dict['price'] = float(template.price)

            result = ApiResult('获取学术服务详情成功', payload={
                'service': service_dict
            })
            return make_response(result.to_response())

    def patch(self):
        with session_scope() as session:
            uuid = self.get_post_data('uuid', require=True, error_message='缺少uuid字段')

            service = session.query(Service).filter(Service.uuid == uuid).first()
            if service is None:
                raise exception.api.NotFound('学术服务不存在')

            if service.user_uuid != self.user_uuid:
                raise exception.api.Forbidden('无权修改其他用户的学术服务')

            auto_renew = self.get_post_data('auto_renew')
            if self.valid_data(auto_renew):
                self.patch_service_auto_renew(service)

            result = ApiResult('修改套餐成功', 201)
            return result.to_response()

    @staticmethod
    def patch_service_auto_renew(service: Service):
        if service.type == service.TYPE.MONTHLY:
            latter_auto_renew_status = 1 if service.auto_renew == 0 else 0
            service.auto_renew = latter_auto_renew_status


view = ServiceAPI

bp = Blueprint(__name__.split('.')[-1], __name__)
root = derive_import_root(__name__)
add_url_rules_for_blueprint(root, bp)
