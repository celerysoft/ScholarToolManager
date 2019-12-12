import base64
import hashlib
from datetime import datetime, timedelta

import configs
from application.model.service import Service
from application.model.service_template import ServiceTemplate
from application.model.subscribe_service_snapshot import SubscribeServiceSnapshot
from application.model.trade_order import TradeOrder
import application.module.payment.scholar.app as scholar_payment_system_app
from application.util import date_util, background_task
from application.util.database import session_scope


class ScholarPaymentSystemToolkit(object):
    _app_id = configs.SCHOLAR_PAYMENT_SYSTEM_APP_ID
    _app_secret = configs.SCHOLAR_PAYMENT_SYSTEM_APP_SECRET

    @staticmethod
    def _derive_timestamp(dt: datetime):
        return dt.strftime('%s')

    @staticmethod
    def _sha1_encrypt(plaintext: str):
        """
        将明文字符串使用SHA1算法进行散列
        :param plaintext:
        :return:
        """
        sha1 = hashlib.sha1()
        sha1.update(plaintext.encode())
        return sha1.hexdigest().upper()

    @staticmethod
    def _md5_encrypt(plaintext: str):
        md5 = hashlib.md5()
        md5.update(plaintext.encode())
        return md5.hexdigest().upper()

    def _derive_signature(self, timestamp):
        return base64.b64encode(
            self._sha1_encrypt(
                self._app_id
                + self._md5_encrypt(timestamp)
                + self._sha1_encrypt(self._app_secret)
            ).encode()
        ).decode()

    def recharge(self, user_uuid: str, amount: float):
        timestamp = self._derive_timestamp(datetime.now())

        signature = self._derive_signature(timestamp)

        payload = {
            'app_id': self._app_id,
            'timestamp': timestamp,
            'user_uuid': user_uuid,
            'amount': amount,
            'signature': signature
        }

        scholar_payment_system_app.recharge(payload)

    def pay_order(self, order_uuid: str):
        # TODO 支付订单

        self.create_service_by_order_uuid(order_uuid)

    def create_service_by_order_uuid(self, order_uuid: str):
        with session_scope() as session:
            order = session.query(TradeOrder) \
                .filter(TradeOrder.uuid == order_uuid,
                        TradeOrder.status != TradeOrder.STATUS.DELETED.value).first()  # type: TradeOrder
            if order is None:
                raise RuntimeError('订单不存在，无法创建学术服务')
            if order.status != order.STATUS.VALID.value:
                raise RuntimeError('订单尚未完成支付，无法创建学术服务')

            # snapshot = session.query(SubscribeServiceSnapshot) \
            #     .filter(SubscribeServiceSnapshot.trade_order_uuid == order_uuid) \
            #     .first()  # type: SubscribeServiceSnapshot
            #
            # service_template = session.query(ServiceTemplate) \
            #     .filter(ServiceTemplate.uuid == snapshot.service_template_uuid).first()  # type: ServiceTemplate
            query_result = session.query(ServiceTemplate, SubscribeServiceSnapshot) \
                .filter(ServiceTemplate.uuid == SubscribeServiceSnapshot.service_template_uuid,
                        SubscribeServiceSnapshot.trade_order_uuid == order_uuid) \
                .first()
            service_template = query_result.ServiceTemplate  # type: ServiceTemplate
            snapshot = query_result.SubscribeServiceSnapshot  # type: SubscribeServiceSnapshot

            service = session.query(Service) \
                .filter(~Service.status.in_([Service.STATUS.DELETED, Service.STATUS.INVALID])) \
                .order_by(Service.port.desc()).first()  # type: Service
            if service is None:
                port = configs.SERVICE_MIN_PORT
            else:
                port = service.port + 1

            # 创建服务
            service_type = service_template.type
            now = datetime.now()
            last_reset_at = None
            auto_renew = None
            if service_type == Service.TYPE.MONTHLY:
                auto_renew = snapshot.auto_renew
                reset_at = date_util.toolkit.derive_1st_datetime_of_next_month(now)
                if auto_renew:
                    expired_at = datetime(2099, 12, 31, 23, 59, 59)
                else:
                    expired_at = reset_at
            elif service_type == Service.TYPE.DATA:
                reset_at = None
                expired_at = now + timedelta(days=365)
            else:
                raise RuntimeError('未知套餐类型')

            service = Service(
                user_uuid=snapshot.user_uuid,
                template_uuid=service_template.uuid,
                service_type=service_type,
                usage=0,
                package=service_template.package,
                auto_renew=auto_renew,
                reset_at=reset_at,
                last_reset_at=last_reset_at,
                expired_at=expired_at,
                total_usage=0,
                port=port,
                password=snapshot.service_password,
            )
            session.add(service)

            background_task.add_port.delay(port=port, password=snapshot.service_password)


toolkit = ScholarPaymentSystemToolkit()
