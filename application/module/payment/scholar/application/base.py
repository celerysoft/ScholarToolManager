import base64
import hashlib

from application.model.scholar_payment_account_log import ScholarPaymentAccountLog


class BaseComponent(object):
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

    def _derive_signature(self, timestamp, app_id, app_secret):
        return base64.b64encode(
            self._sha1_encrypt(
                app_id
                + self._md5_encrypt(timestamp)
                + self._sha1_encrypt(app_secret)
            ).encode()
        ).decode()

    @classmethod
    def increase(cls, session, account_uuid, old_balance, amount, new_balance,
                 purpose_type: ScholarPaymentAccountLog.PurposeType) -> ScholarPaymentAccountLog:
        if new_balance - old_balance != amount:
            raise RuntimeError('非法请求')
        return cls.create_scholar_payment_account_log(
            session=session,
            account_uuid=account_uuid,
            old_balance=old_balance,
            amount=amount,
            new_balance=new_balance,
            log_type=ScholarPaymentAccountLog.Type.INCREASE,
            purpose_type=purpose_type,
        )

    @classmethod
    def decrease(cls, session, account_uuid, old_balance, amount, new_balance,
                 purpose_type: ScholarPaymentAccountLog.PurposeType) -> ScholarPaymentAccountLog:
        if old_balance - new_balance != amount:
            raise RuntimeError('非法请求')
        return cls.create_scholar_payment_account_log(
            session=session,
            account_uuid=account_uuid,
            old_balance=old_balance,
            amount=amount,
            new_balance=new_balance,
            log_type=ScholarPaymentAccountLog.Type.DECREASE,
            purpose_type=purpose_type,
        )

    @staticmethod
    def create_scholar_payment_account_log(session, account_uuid: str, old_balance, amount, new_balance,
                                           log_type: ScholarPaymentAccountLog.Type,
                                           purpose_type: ScholarPaymentAccountLog.PurposeType) \
            -> ScholarPaymentAccountLog:
        log = ScholarPaymentAccountLog(
            account_uuid=account_uuid,
            former_balance=old_balance,
            amount=amount,
            balance=new_balance,
            log_type=log_type.value,
            purpose_type=purpose_type.value,
        )
        session.add(log)
        session.flush()
        return log
