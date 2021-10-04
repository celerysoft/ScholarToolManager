# -*- coding: utf-8 -*-
"""
A toolkit for user authorization
"""
import hashlib
from datetime import timedelta, datetime

import jwt

import configs
from application.util.snowflake import snowflake_toolkit


class AuthorizationToolkit(object):
    @staticmethod
    def hash_plaintext(password) -> str:
        """
        Hash the password as plaintext
        :return: encryption password
        """
        sha256 = hashlib.sha256()
        salt = configs.PASSWORD_SALT

        sha256.update(salt.encode('utf-8'))
        sha256.update(b':')
        sha256.update(password.encode('utf-8'))
        sha256.update(b':')
        sha256.update(salt.encode('utf-8'))

        return sha256.hexdigest()

    @staticmethod
    def derive_jwt_token(user_id: int, user_uuid: str, expired_in: int = 24, extra_payload: dict = None) -> str:
        """
        为用户生成jwt

        :param user_id: 用户id
        :param user_uuid: 用户uuid
        :param expired_in: 过期时间（小时）
        :param extra_payload: 额外的payload
        :return: 用户的jwt
        """
        now = datetime.now()

        payload = {
            'id': user_id,
            'uuid': user_uuid,
            'issuer': 'https://www.celerysoft.science',
            'iat': int(now.timestamp()),
            'nbf': int(now.timestamp()),
            'exp': int((now + timedelta(hours=expired_in)).timestamp()),
            'jti': snowflake_toolkit.get_id_from_default_worker()
        }
        if extra_payload is not None:
            for k, v in extra_payload.items():
                payload[k] = v

        jwt_token = jwt.encode(payload, configs.JWT_SECRET, algorithm='HS256')

        return jwt_token.decode('utf8')

    @staticmethod
    def decode_jwt_token(jwt_token):
        return jwt.decode(jwt_token, configs.JWT_SECRET, algorithms='HS256')


toolkit = AuthorizationToolkit()
authorization_toolkit = toolkit
