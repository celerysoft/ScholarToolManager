import base64
import hashlib
from datetime import datetime

import configs
import application.module.payment.scholar.app as scholar_payment_system_app


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

        scholar_payment_system_app.recharge.delay(payload)

    def pay_order(self, trade_order_uuid: str):
        timestamp = self._derive_timestamp(datetime.now())

        signature = self._derive_signature(timestamp)

        payload = {
            'app_id': self._app_id,
            'timestamp': timestamp,
            'trade_order_uuid': trade_order_uuid,
            'signature': signature
        }

        scholar_payment_system_app.subscribe_service.delay(payload)


toolkit = ScholarPaymentSystemToolkit()
