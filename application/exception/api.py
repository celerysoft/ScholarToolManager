# -*-coding:utf-8 -*-
import json

from flask import Response


class BaseApiException(Exception):
    STATUS_CODE = 500

    def __init__(self, message, payload=None):
        Exception.__init__(self)
        self.message = message
        self.payload = payload

    def to_response(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return Response(json.dumps(rv),
                        status=self.STATUS_CODE,
                        mimetype='application/json')


class InvalidRequest(BaseApiException):
    STATUS_CODE = 400

    def __init__(self, message, payload=None):
        BaseApiException.__init__(self, message, payload=payload)


class Unauthorized(BaseApiException):
    STATUS_CODE = 401

    def __init__(self, message, payload=None):
        BaseApiException.__init__(self, message, payload=payload)


class Forbidden(BaseApiException):
    STATUS_CODE = 403

    def __init__(self, message, payload=None):
        BaseApiException.__init__(self, message, payload=payload)


class NotFound(BaseApiException):
    STATUS_CODE = 404

    def __init__(self, message, payload=None):
        BaseApiException.__init__(self, message, payload=payload)


class Conflict(BaseApiException):
    STATUS_CODE = 409

    def __init__(self, message, payload=None):
        BaseApiException.__init__(self, message, payload=payload)


class InternalServerError(BaseApiException):
    STATUS_CODE = 500

    def __init__(self, message, payload=None):
        BaseApiException.__init__(self, message, payload=payload)


class ServiceUnavailable(BaseApiException):
    STATUS_CODE = 403

    def __init__(self, message, payload=None):
        BaseApiException.__init__(self, message, payload=payload)
