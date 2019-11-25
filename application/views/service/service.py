# -*- coding: utf-8 -*-
from datetime import datetime

from flask import make_response, Blueprint

import configs
from app import derive_import_root, add_url_rules_for_blueprint
from application import exception
from application.model.legacy.model import to_dict2, Service, ServiceTemplate, \
    ServicePassword, UserService, UserScholarBalance, UserScholarBalanceLog
from application.util import permission, date_util, background_task
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


class ServiceAPI(BaseNeedLoginAPI):
    methods = ['GET', 'POST', 'PATCH']

    def get(self):
        service_id = self.get_data('id')
        if self.valid_data(service_id):
            return self.get_service_by_id(service_id)
        else:
            return self.get_user_services(self.user_id)

    def get_user_services(self, user_id):
        with session_scope() as db_session:

            query = db_session.query(Service) \
                .filter(UserService.user_id == user_id) \
                .filter(UserService.service_id == Service.id)

            page, page_size, offset, max_page = self._derive_page_parameter(query.count())

            services = query.offset(offset).limit(page_size).all()

            service_list = []

            for s in services:
                service = to_dict2(s)
                template = db_session.query(ServiceTemplate).filter(ServiceTemplate.id == s.template_id).first()
                service_password = db_session.query(ServicePassword) \
                    .filter(ServicePassword.service_id == s.id).first()
                service['title'] = template.title
                service['price'] = template.price
                service['port'] = service_password.port
                service_list.append(service)

        result = ApiResult('获取用户套餐信息成功', payload={
            'page': page,
            'page_size': page_size,
            'max_page': max_page,
            'service': service_list
        })
        return make_response(result.to_response())

    def get_service_by_id(self, service_id):
        with session_scope() as session:
            service = session.query(Service).filter(Service.id == service_id).first()
            if service is None:
                raise exception.api.NotFound('指定id的套餐不存在')

            template = session.query(ServiceTemplate) \
                .filter(ServiceTemplate.id == service.template_id).first()
            service_password = session.query(ServicePassword) \
                .filter(ServicePassword.service_id == service.id).first()
            service_dict = to_dict2(service)
            service_dict['type'] = template.type
            service_dict['title'] = template.title
            service_dict['price'] = template.price
            service_dict['port'] = service_password.port
            service_dict['password'] = service_password.password
            if template.type == ServiceTemplate.MONTHLY:
                service_dict['renew_at'] = date_util.toolkit.datetime_to_str(service.reset_at)
            else:
                service_dict['renew_at'] = date_util.toolkit.datetime_to_str(service.expired_at)

        result = ApiResult('获取套餐详情成功', payload={
            'service': service_dict
        })
        return make_response(result.to_response())

    def post(self):
        service_template_id = self.get_post_data('template_id', require=True, error_message='缺少template_id字段')
        password = self.get_post_data('password', require=True, error_message='缺少password字段')

        with session_scope() as session:
            if not permission.check_manage_service_permission(session, self.user_id, True):
                raise exception.api.Forbidden("无权创建套餐")

            service_template = session.query(ServiceTemplate) \
                .filter(ServiceTemplate.id == service_template_id).first()
            if not service_template.available:
                raise exception.api.Forbidden('该套餐已下架，故无法办理')

            # 扣费
            total_payment = service_template.initialization_fee + service_template.price
            user_scholar_balance = session.query(UserScholarBalance) \
                .filter(UserScholarBalance.user_id == self.user_id).first()
            balance = user_scholar_balance.balance
            if balance < total_payment:
                raise exception.api.Forbidden('余额不足，创建套餐失败')
            else:
                user_scholar_balance.balance -= total_payment

                user_scholar_balance_log = UserScholarBalanceLog(
                    user_id=user_scholar_balance.user_id,
                    amount=(-total_payment),
                    balance=user_scholar_balance.balance,
                    message='新购套餐：{}'.format(service_template.title)
                )
                session.add(user_scholar_balance_log)

            # 创建服务
            service_type = service_template.type
            now = datetime.now()
            created_at = now
            last_reset_at = None
            auto_renew = None
            if service_type == ServiceTemplate.MONTHLY:
                auto_renew = self.get_post_data('auto_renew', require=True, error_message='缺少auto_renew字段')
                reset_at = date_util.toolkit.derive_1st_datetime_of_next_month(now)
                if auto_renew:
                    expired_at = datetime(2099, 12, 31, 23, 59, 59)
                else:
                    expired_at = reset_at
            elif service_type == ServiceTemplate.DATA:
                reset_at = None
                expired_at = datetime.fromtimestamp(created_at.timestamp() + 365 * 24 * 60 * 60)
            else:
                raise exception.api.NotFound('未知套餐类型')

            service = Service(
                template_id=service_template_id,
                type=service_type,
                usage=0,
                last_usage=0,
                package=service_template.balance,
                reset_at=reset_at,
                last_reset_at=last_reset_at,
                created_at=created_at,
                expired_at=expired_at,
                total_usage=0,
                auto_renew=auto_renew
            )
            session.add(service)
            session.flush()

            service_id = service.id

            # 关联user_service表
            user_service = UserService(self.user_id, service_id)
            session.add(user_service)

            # 关联service_password表
            service_port = self.derive_available_shadowsocks_port(session)

            service_password = ServicePassword(service.id, service_port, password)
            session.add(service_password)

            background_task.add_port.delay(port=service_port, password=password)

        result = ApiResult('创建套餐成功', 201, {
            'service_id': service_id
        })
        return make_response(result.to_response())

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
