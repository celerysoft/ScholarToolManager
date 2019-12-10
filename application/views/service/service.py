# -*- coding: utf-8 -*-
from datetime import datetime

from flask import make_response, Blueprint

import configs
from app import derive_import_root, add_url_rules_for_blueprint
from application import exception
from application.model.legacy.model import ServicePassword, UserService, UserScholarBalance, UserScholarBalanceLog
from application.model.service import Service
from application.model.service_template import ServiceTemplate
from application.util import date_util, background_task
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


class ServiceAPI(BaseNeedLoginAPI):
    methods = ['GET', 'POST', 'PATCH', 'PUT']

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
                .filter(Service.status != Service.STATUS.DELETED)

            page, page_size, offset, max_page = self._derive_page_parameter(query.count())

            services = query.offset(offset).limit(page_size).all()

            service_list = []
            for record in services:  # type:ServiceTemplate
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
            if template.type == Service.TYPE.MONTHLY:
                service_dict['renew_at'] = date_util.toolkit.datetime_to_str(service.reset_at)
            else:
                service_dict['renew_at'] = date_util.toolkit.datetime_to_str(service.expired_at)

        result = ApiResult('获取学术服务详情成功', payload={
            'service': service_dict
        })
        return make_response(result.to_response())

    def post(self):
        if configs.DEBUG:
            raise exception.api.ServiceUnavailable('网站更新中，暂停开通新的学术服务')

        result = ApiResult('创建服务成功', 201)
        return result.to_response()

    def derive_available_shadowsocks_port(self, db_session):
        service_password = db_session.query(ServicePassword) \
            .order_by(ServicePassword.port.desc()) \
            .filter(Service.alive.is_(True)) \
            .filter(Service.id == ServicePassword.service_id).first()

        if service_password is None:
            return configs.SERVICE_MIN_PORT
        else:
            return service_password.port + 1

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
            service.reset_at = date_util.toolkit.derive_1st_datetime_of_next_month(datetime.now())
            if latter_auto_renew_status == 1:
                service.expired_at = datetime(2099, 12, 31, 23, 59, 59)
            elif latter_auto_renew_status == 0:
                service.expired_at = service.reset_at

    def put(self):
        with session_scope() as session:
            service_id = self.get_post_data('id', require=True, error_message='缺少id字段')
            auto_renew = self.get_post_data('auto_renew')
            renew = self.get_post_data('renew')

            user_service = session.query(UserService) \
                .filter(UserService.user_id == self.user_id) \
                .filter(UserService.service_id == service_id).first()
            if user_service is None:
                raise exception.api.Forbidden('无权修改他人的套餐')

            service = session.query(Service) \
                .filter(Service.id == service_id).first()
            if service is None:
                raise exception.api.NotFound('套餐不存在')

            service_template_id = service.template_id
            service_template = session.query(ServiceTemplate) \
                .filter(ServiceTemplate.id == service_template_id).first()

            # 修改自动续费
            now = datetime.now()
            if auto_renew is not None and service_template.type == ServiceTemplate.MONTHLY:
                service.auto_renew = auto_renew
                service.reset_at = date_util.toolkit.derive_1st_datetime_of_next_month(now)
                if auto_renew:
                    service.expired_at = datetime(2099, 12, 31, 23, 59, 59)
                else:
                    service.expired_at = service.reset_at

            # 续费
            if renew is not None and renew is True:
                if not service_template.available:
                    return self.api_document('该套餐已下架，无法办理续费', 403)

                # 判断是否还可以续费
                if not service.alive:
                    return self.api_document('由于长期没有续费，该套餐已经被系统释放，无法进行续费操作，如有需要请新开学术套餐')

                # 判断是否在可续费时间内
                if service_template.type == ServiceTemplate.MONTHLY:
                    if service.reset_at.timestamp() < now.timestamp() < (service.reset_at.timestamp() + 24 * 60 * 60):
                        pass
                    else:
                        return self.api_document('当前不是有效的续费时间，请在每月1号进行续费')
                elif service_template.type == ServiceTemplate.DATA:
                    if (service.package - service.usage <= service.package * 0.2
                        and now.timestamp() < service.expired_at.timestamp()) \
                            or (service.expired_at.timestamp() < now.timestamp() <
                                date_util.toolkit.derive_1st_of_next_month(service.expired_at)):
                        pass
                    else:
                        return self.api_document('当前不是有效的续费时间，或者剩余流量大于总流量的20%，无法续费')

                # 扣费
                total_payment = service_template.price
                user_scholar_balance = session.query(UserScholarBalance) \
                    .filter(UserScholarBalance.user_id == self.user_id).first()
                balance = user_scholar_balance.balance
                if balance < total_payment:
                    return self.api_document('学术积分余额不足，无法续费', 403)
                else:
                    user_scholar_balance.balance -= total_payment

                    user_scholar_balance_log = UserScholarBalanceLog(
                        user_id=user_scholar_balance.user_id,
                        amount=(-total_payment),
                        balance=user_scholar_balance.balance,
                        message='套餐续费，套餐id: %s，套餐名称：%s' % (service.id, service_template.title)
                    )
                    session.add(user_scholar_balance_log)

                # 更新服务
                service.last_reset_at = now
                service.usage = 0
                if not service.available:
                    service.available = True
                    service_password = session.query(ServicePassword) \
                        .filter(ServicePassword.service_id == service_id).first()
                    background_task.add_port.delay(port=service_password.port, password=service_password.password)
                if service_template.type == ServiceTemplate.MONTHLY:
                    auto_renew = self.get_post_data('auto_renew', require=True, error_message='缺少auto_renew字段')
                    if auto_renew:
                        service.reset_at = date_util.toolkit.derive_1st_datetime_of_next_month(now)
                        service.expired_at = datetime(2099, 12, 31, 23, 59, 59)
                    else:
                        service.reset_at = None
                        service.expired_at = date_util.toolkit.derive_1st_of_next_month(now)
                elif service_template.type == ServiceTemplate.DATA:
                    service.expired_at = datetime.fromtimestamp(now.timestamp() + 365 * 24 * 60 * 60)

        result = ApiResult('更新套餐成功', 201)
        return make_response(result.to_response())


view = ServiceAPI

bp = Blueprint(__name__.split('.')[-1], __name__)
root = derive_import_root(__name__)
add_url_rules_for_blueprint(root, bp)
