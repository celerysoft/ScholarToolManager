# -*- coding: utf-8 -*-
from typing import Union

from flask import make_response

from application import exception
from application.model.service_template import ServiceTemplate
from application.util import permission
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


class ServiceTemplateAPI(BaseNeedLoginAPI):
    methods = ['GET', 'POST', 'PATCH', 'DELETE']

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
                                                          ServiceTemplate.status != ServiceTemplate.STATUS.DELETED)
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
                        ServiceTemplate.status != ServiceTemplate.STATUS.DELETED) \
                .order_by(ServiceTemplate.created_at.desc()).limit(size).all()

            data_templates = session.query(ServiceTemplate) \
                .filter(ServiceTemplate.type == ServiceTemplate.TYPE.DATA,
                        ServiceTemplate.status != ServiceTemplate.STATUS.DELETED) \
                .order_by(ServiceTemplate.created_at.desc()).limit(size).all()

            result = ApiResult('获取服务模板信息成功', 200, {
                'monthly_services': self.models_to_list(monthly_templates),
                'data_services': self.models_to_list(data_templates),
            })
            return result.to_response()

    def post(self):
        service_type = self.get_post_data('type', require=True, error_message='缺少type字段')
        title = self.get_post_data('title', require=True, error_message='缺少title字段')
        subtitle = self.get_post_data('subtitle', require=True, error_message='缺少subtitle字段')
        description = self.get_post_data('description', require=True, error_message='缺少description字段')
        balance = self.get_post_data('balance', require=True, error_message='缺少balance字段')
        price = self.get_post_data('price', require=True, error_message='缺少price字段')
        initialization_fee = self.get_post_data('initialization_fee', require=True,
                                                error_message='缺少initialization_fee字段')

        with session_scope() as session:
            if not permission.toolkit.check_manage_service_template_permission(session, self.user_id):
                raise exception.api.Forbidden('当前户无权创建套餐模版')

            service_template = ServiceTemplate(service_type, title, subtitle, description, balance, price,
                                               initialization_fee)
            session.add(service_template)

        result = ApiResult('创建套餐模板成功', 201)
        return make_response(result.to_response())

    def patch(self):
        service_id = self.get_post_data('id', require=True, error_message='缺少id字段')
        service_type = self.get_post_data('type', require=True, error_message='缺少type字段')
        title = self.get_post_data('title', require=True, error_message='缺少title字段')
        subtitle = self.get_post_data('subtitle', require=True, error_message='缺少subtitle字段')
        description = self.get_post_data('description', require=True, error_message='缺少description字段')
        balance = self.get_post_data('balance', require=True, error_message='缺少balance字段')
        price = self.get_post_data('price', require=True, error_message='缺少price字段')
        initialization_fee = self.get_post_data('initialization_fee', require=True,
                                                error_message='缺少initialization_fee字段')
        available = self.get_post_data('available', require=True, error_message='缺少available字段')

        with session_scope() as db_session:
            if not permission.toolkit.check_manage_service_template_permission(db_session, self.user_id):
                raise exception.api.Forbidden('用户无权修改套餐模版')

            service_template = db_session.query(ServiceTemplate).filter(ServiceTemplate.id == service_id).first()
            if service_template is None:
                raise exception.api.NotFound('套餐模版不存在')

            service_template.type = service_type
            service_template.title = title
            service_template.subtitle = subtitle
            service_template.description = description
            service_template.balance = balance
            service_template.price = price
            service_template.initialization_fee = initialization_fee
            service_template.available = available

        result = ApiResult('编辑套餐模板成功', 201)
        return make_response(result.to_response())

    def delete(self):
        service_template_id = self.get_post_data('id', require=True, error_message='缺少id字段')

        with session_scope() as session:
            if not permission.toolkit.check_manage_service_template_permission(session, self.user_id):
                raise exception.api.Forbidden('当前户无权创建套餐模版')

            service_template = session.query(ServiceTemplate).filter(
                ServiceTemplate.id == service_template_id).first()

            service_count = session.query(Service).filter(Service.alive.is_(True),
                                                     Service.template_id == service_template_id).count()
            if service_count > 0:
                raise exception.api.Conflict('还有{}个存活套餐使用该套餐模板，故无法删除'.format(service_count))
            else:
                session.delete(service_template)

        result = ApiResult('删除套餐模板成功')
        return make_response(result.to_response())


view = ServiceTemplateAPI
