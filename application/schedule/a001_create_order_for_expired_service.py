# -*-coding:utf-8 -*-
"""
过期服务自动生成续费订单的脚本
执行频率：每天执行
执行优先级：A-1
"""
from datetime import datetime

from application.model.service import Service
from application.model.service_template import ServiceTemplate
from application.model.service_trade_order import ServiceTradeOrder
from application.model.subscribe_service_snapshot import SubscribeServiceSnapshot
from application.model.trade_order import TradeOrder
from application.util import trade_order
from application.util.database import session_scope


class CreateOrderForExpiredServiceScript:
    def execute(self):
        now = datetime.now()
        if now.day == 1:
            self.create_order_for_monthly_service(now)
        self.create_order_for_data_service(now)

    def create_order_for_service(self, service_type: Service.TYPE, now: datetime):
        with session_scope() as session:
            services = session.query(Service) \
                .filter(Service.type == service_type,
                        Service.status.in_([Service.STATUS.INITIALIZATION, Service.STATUS.ACTIVATED,
                                            Service.STATUS.SUSPENDED]),
                        Service.billing_date <= now)
            for service in services:  # type: Service
                conflict, snapshot = trade_order.toolkit.check_is_order_conflict(
                    session, service.user_uuid, service_uuid=service.uuid,
                )
                if conflict:
                    print('有尚未支付的『{}』的订单，请勿重复下单'.format(snapshot.title))
                    continue

                service_template = session.query(ServiceTemplate) \
                    .filter(ServiceTemplate.uuid == service.template_uuid,
                            ServiceTemplate.status != ServiceTemplate.STATUS.DELETED).first()  # type: ServiceTemplate
                if service_template is None:
                    print('套餐不存在，无法办理')
                    continue
                if service_template.status == ServiceTemplate.STATUS.SUSPEND:
                    print('该套餐已下架，无法办理')
                    continue

                total_payment = service_template.price

                order = TradeOrder(
                    user_uuid=service.user_uuid,
                    order_type=TradeOrder.TYPE.CONSUME.value,
                    amount=total_payment,
                    description='续费学术服务，服务UUID：{}'.format(service.uuid)
                )
                session.add(order)
                session.flush()

                snapshot = SubscribeServiceSnapshot(
                    trade_order_uuid=order.uuid,
                    user_uuid=service.user_uuid,
                    service_password=service.password,
                    auto_renew=service.auto_renew,
                    service_template_uuid=service.template_uuid,
                    service_type=service.type,
                    title=service_template.title,
                    subtitle=service_template.subtitle,
                    description=service_template.description,
                    package=service_template.package,
                    price=service_template.price,
                    initialization_fee=service_template.initialization_fee
                )
                session.add(snapshot)

                relationship = ServiceTradeOrder(
                    service_uuid=service.uuid,
                    trade_order_uuid=order.uuid,
                )
                session.add(relationship)

    def create_order_for_monthly_service(self, now: datetime):
        self.create_order_for_service(Service.TYPE.MONTHLY, now)

    def create_order_for_data_service(self, now: datetime):
        self.create_order_for_service(Service.TYPE.DATA, now)


if __name__ == '__main__':
    script = CreateOrderForExpiredServiceScript()
    script.execute()
