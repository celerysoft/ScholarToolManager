import base64
import hashlib


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
