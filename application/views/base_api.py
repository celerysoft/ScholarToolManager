# -*- coding: utf-8 -*-
import json
import math

from flask import request, Response, session
from flask.views import MethodView
# from jwt import PyJWTError

import configs
from application import exception
# from application.toolkit.authorization import decode_jwt_token
# from application.util.database import session_scope
# from application.models.user import User
# from application.toolkits.authorization import decode_jwt_token
# from application.toolkits.cache import cache
# from application.toolkits.task_queue import queue


class ApiResult(object):
    def __init__(self, message, status=200, payload=None):
        self.message = message
        self.status = status
        self.payload = payload

    def to_response(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return Response(json.dumps(rv),
                        status=self.status,
                        mimetype='application/json')


class BaseView(MethodView):
    user_id = ''

    @classmethod
    def _derive_page_parameter(cls, record_count):
        default_items_per_page = 10
        page = request.args.get('page', 1)
        try:
            page = int(page) if page is not None else 1
        except ValueError:
            raise exception.api.InvalidRequest('Invalid page field.')
        page_size = request.args.get('page_size', 10)
        try:
            page_size = int(page_size) if page_size is not None else default_items_per_page
        except ValueError:
            page_size = default_items_per_page

        offset = (page - 1) * page_size

        if 0 < record_count <= offset:
            # noinspection PyUnresolvedReferences
            raise exception.api.InvalidRequest('Item index is out of bounds, try modify page and page_size.')
        max_page = math.ceil(record_count / page_size)

        return page, page_size, offset, max_page

    @staticmethod
    def _derive_get_method_query_dict(model_class):
        fields = []
        for field in model_class.__table__.columns:
            fields.append(field.name)
        query_dict = {}
        for key, value in request.args.items():
            if key in ['page', 'page_size']:
                continue
            if value in [None, '']:
                continue
            if key in fields:
                query_dict[key] = value
        return query_dict

    @staticmethod
    def get_data(key, req=request):
        return req.args.get(key, None)

    @staticmethod
    def get_post_data(key, req=request):
        post_data = None
        if req.json is not None:
            post_data = req.json.get(key, None)
        else:
            post_data = req.form.get(key, None)
        return post_data

    @staticmethod
    def get_file_data(key, req=request):
        file_data = None
        if key in req.files:
            file_data = req.files.get(key, None)
        return file_data

    @classmethod
    def valid_data(cls, data) -> bool:
        if type(data) == str:
            return data is not None and len(data) > 0
        else:
            return data is not None

    @classmethod
    def patch_model(cls, model_class, model, data: dict = None, *args, exclude=None):

        if exclude is None:
            exclude = []
        if model_class.__immutable_columns__ is not None:
            exclude.extend(model_class.__immutable_columns__)

        fields = []
        for field in model_class.__table__.columns:
            fields.append(field.name)

        if args is None or len(args) == 0:
            args = fields

        for arg in args:
            if arg in exclude:
                continue

            if data is None:
                value = cls.get_post_data(arg)
            else:
                value = data.get(arg)

            if cls.valid_data(value) and arg in fields:
                setattr(model, arg, value)

    # def check_jwt(self) -> str:
    #     """
    #     check if user login or not
    #
    #     :return: user's uuid
    #     """
    #     if hasattr(self, 'uuid') and len(self.uuid) > 0:
    #         return self.uuid
    #
    #     jwt = request.headers.get('Authorization', None)
    #     if jwt is None or len(jwt) == 0:
    #         return ''
    #
    #     try:
    #         decoded_jwt = decode_jwt_token(jwt)
    #     except PyJWTError:
    #         return ''
    #
    #     with session_scope() as session:
    #         # user = session.query(User).filter(User.uuid == decoded_jwt['uuid']).first()  # type:User
    #         # self.uuid = user.uuid
    #         # return user.uuid
    #         self.uuid = decoded_jwt['uuid']
    #         return self.uuid


class BaseAPI(BaseView):
    pass
    # methods = ['GET']

    # def get_single_model(self, model_class, uuid, query, not_found_exception_message='不存在'):
    #     model = cache.get_model(model_class, uuid)
    #     # model = None
    #     if model is None:
    #         model = query.first()
    #         if model is None:
    #             raise exception.api.NotFound(not_found_exception_message)
    #         else:
    #             cache.set_model(model)
    #     return model
    #
    # def get_multiple_models(self):
    #     pass


def jwt_api(func):
    pass
    # def handle_jwt(view: MethodView):
    #     jwt = request.headers.get('Authorization', None)
    #     if jwt is None or len(jwt) == 0:
    #         raise exception.api.Unauthorized('请先登录')
    #
    #     try:
    #         decoded_jwt = decode_jwt_token(jwt)
    #     except PyJWTError as e:
    #         raise exception.api.Unauthorized('请先登录')
    #
    #     with session_scope() as session:
    #         # user = session.query(User).filter(User.id == decoded_jwt['user_id']).first()  # type:User
    #         # view.uuid = user.uuid
    #         view.user_id = decoded_jwt['user_id']
    #
    # def wrapper(*args, **kwargs):
    #     for parameter in args:
    #         if isinstance(parameter, BaseNeedLoginAPI):
    #             if parameter.need_login_methods is not None and request.method in parameter.need_login_methods:
    #                 handle_jwt(parameter)
    #         elif isinstance(parameter, MethodView):
    #             handle_jwt(parameter)
    #     return func(*args, **kwargs)
    #
    # return wrapper


def session_api(func):
    session_dict = session

    def handle_session(view: MethodView):
        if 'user' not in session_dict.keys():
            raise exception.api.Unauthorized('请先登录')

        try:
            user_id = session['user']['id']
        except KeyError:
            raise exception.api.Unauthorized('请先登录')

        view.user_id = user_id

    def wrapper(*args, **kwargs):
        for parameter in args:
            if isinstance(parameter, BaseNeedLoginAPI):
                if parameter.need_login_methods is not None and request.method in parameter.need_login_methods:
                    handle_session(parameter)
            elif isinstance(parameter, MethodView):
                handle_session(parameter)
        return func(*args, **kwargs)

    return wrapper


class BaseNeedLoginAPI(BaseAPI):
    # 需要理用户登录才能执行的方法
    need_login_methods = ['HEAD', 'GET', 'POST', 'PATCH', 'PUT', 'DELETE']

    def dispatch_request(self, *args, **kwargs):
        if request.method in self.need_login_methods:
            self.check_login_status()
        return super(BaseNeedLoginAPI, self).dispatch_request(*args, **kwargs)

    def check_login_status(self):
        try:
            self.check_session()
        except exception.api.Unauthorized as e:
            if not configs.TEST:
                raise e
            else:
                if request.method in ['GET', 'DELETE']:
                    self.user_id = self.get_data('user_id')
                elif request.method in ['POST', 'PATCH', 'PUT']:
                    self.user_id = self.get_post_data('user_id')

                if not self.valid_data(self.user_id):
                    raise e

    @session_api
    def check_session(self):
        pass

    @jwt_api
    def check_jwt(self):
        pass
