# -*-coding:utf-8 -*-
class BaseRequestException(Exception):
    status_code = 500

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class Unauthorized(BaseRequestException):
    def __init__(self, message=None, payload=None):
        BaseRequestException.__init__(self, message, status_code=401, payload=payload)


class Forbidden(BaseRequestException):
    def __init__(self, message=None, payload=None):
        BaseRequestException.__init__(self, message, status_code=403, payload=payload)
