# -*-coding:utf-8 -*-
# from typing import TypeVar

import redis
# from sqlalchemy.orm import class_mapper

import configs
# from application.model.model import Base

# T = TypeVar('T', Base, BaseModel)


class Cache(object):
    r = None  # type redis.Redis

    def __init__(self):
        redis_host = configs.REDIS_HOST
        redis_port = configs.REDIS_PORT
        pool = redis.ConnectionPool(host=redis_host, port=redis_port, decode_responses=True)
        self.r = redis.Redis(connection_pool=pool)

    # def __is_model(self, o) -> bool:
    #     try:
    #         if not isinstance(o, type):
    #             o = o.__class__
    #         class_mapper(o)
    #         return True
    #     except BaseException as e:
    #         print(e)
    #         return False

    def set(self, name, value):
        self.r.set(name, value)

    def get(self, name):
        return self.r.get(name)

    # def set_model(self, value: Base):
    #     key = '{}:{}'.format(value.__tablename__, value.id)
    #     self.r.set(key, value.to_json_string())
    #
    # def get_model(self, model_class: Base, uuid):
    #     key = '{}:{}'.format(model_class.__tablename__, uuid)
    #     json_string = self.r.get(key)
    #     if json_string is not None:
    #         # return None
    #         return model_class.from_json_string(json_string)
    #     return None

    def incr(self, name, amount=1):
        self.r.incr(name, amount)

    def expire(self, name, time):
        self.r.expire(name, time)

    def delete(self, *names):
        self.r.delete(*names)


cache = Cache()
