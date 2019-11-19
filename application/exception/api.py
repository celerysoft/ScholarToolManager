import json

from flask import Response


class BaseApiException(Exception):
    status_code = 500

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_response(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return Response(json.dumps(rv),
                        status=self.status_code,
                        mimetype='application/json')


class InvalidRequest(BaseApiException):
    def __init__(self, message, payload=None):
        BaseApiException.__init__(self, message, status_code=400, payload=payload)


class Unauthorized(BaseApiException):
    def __init__(self, message, payload=None):
        BaseApiException.__init__(self, message, status_code=401, payload=payload)


class Forbidden(BaseApiException):
    def __init__(self, message, payload=None):
        BaseApiException.__init__(self, message, status_code=403, payload=payload)


class InternalServerError(BaseApiException):
    def __init__(self, message, payload=None):
        BaseApiException.__init__(self, message, status_code=500, payload=payload)
