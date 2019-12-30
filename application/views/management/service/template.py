# -*- coding: utf-8 -*-
from application import exception
from application.model.service_template import ServiceTemplate
from application.util.database import session_scope
from application.views.base_api import PermissionRequiredAPI, ApiResult


class ManagementServiceTemplateAPI(PermissionRequiredAPI):
    methods = ['GET', 'POST', 'PUT', 'DELETE']
    permission_required_for_get = []
    permission_required_for_post = []
    permission_required_for_delete = []

    def get(self):
        with session_scope() as session:
            template_list = []
            query = self.derive_query_for_get_method(session, ServiceTemplate) \
                .filter(ServiceTemplate.status != ServiceTemplate.STATUS.DELETED)
            page, page_size, offset, max_page = self.derive_page_parameter(query.count())
            templates = query.limit(page_size).offset(offset).all()
            for template in templates:  # type: ServiceTemplate
                # template_dict = template.to_dict()
                # template_list.append(template_dict)
                template_list.append(template.to_dict())

            result = ApiResult('获取学术服务信息成功', payload={
                'templates': template_list,
                'page': page,
                'page_size': page_size,
                'max_page': max_page,
            })
            return result.to_response()

    def post(self):
        # service_type = self.get_post_data('type', require=True, error_message='缺少type字段')
        # title = self.get_post_data('title', require=True, error_message='缺少title字段')
        # subtitle = self.get_post_data('subtitle', require=True, error_message='缺少subtitle字段')
        # description = self.get_post_data('description', require=True, error_message='缺少description字段')
        # package = self.get_post_data('package', require=True, error_message='缺少package字段')
        # try:
        #     package = int(package)
        # except:
        #     raise exception.api.InvalidRequest('请输入合法的package字段')
        # price = self.get_post_data('price', require=True, error_message='缺少price字段')
        # try:
        #     price = float(price)
        # except:
        #     raise exception.api.InvalidRequest('请输入合法的price字段')
        # initialization_fee = self.get_post_data('initialization_fee', require=True,
        #                                         error_message='缺少initialization_fee字段')
        # try:
        #     initialization_fee = float(initialization_fee)
        # except:
        #     raise exception.api.InvalidRequest('请输入合法的initialization_fee字段')
        #
        # with session_scope() as session:
        #     template = ServiceTemplate(
        #         service_type=service_type,
        #         title=title,
        #         subtitle=subtitle,
        #         description=description,
        #         package=package,
        #         price=price,
        #         initialization_fee=initialization_fee,
        #     )
        #     session.add(template)
        #     session.flush()
        #
        #     result = ApiResult('创建学术服务模板成功', 201, payload={
        #         'template': template.to_dict(),
        #     })
        #     return result.to_response()
        with session_scope() as session:
            template = self.create_model_from_http_post(ServiceTemplate)
            session.add(template)
            session.flush()

            result = ApiResult('创建学术服务模板成功', 201, payload={
                'template': template.to_dict(),
            })
            return result.to_response()

    def put(self):
        with session_scope() as session:
            template = self.update_model(session, ServiceTemplate)

            result = ApiResult('修改学术服务模板成功', 200, payload={
                'template': template.to_dict(),
            })
            return result.to_response()

    def delete(self):
        uuid = self.get_data('uuid', require=True, error_message='请输入uuid字段')

        with session_scope() as session:
            template = session.query(ServiceTemplate) \
                .filter(ServiceTemplate.uuid == uuid,
                        ServiceTemplate.status != ServiceTemplate.STATUS.DELETED) \
                .first()  # type: ServiceTemplate

            if template is None:
                raise exception.api.NotFound('需要删除的学术服务模板不存在')

            template.status = 2

            result = ApiResult('删除学术服务模板成功')
            return result.to_response()


view = ManagementServiceTemplateAPI
