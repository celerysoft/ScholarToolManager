import json
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, func
from sqlalchemy.dialects.mysql import TINYINT, VARCHAR, DATETIME, INTEGER
from sqlalchemy.ext.declarative import declarative_base, declared_attr


class TimestampMixin(object):
    created_at = Column(DATETIME, nullable=False, default=func.now(), server_default=func.now())
    updated_at = Column(DATETIME, nullable=False, default=func.now(), server_default=func.now(), onupdate=func.now())


class IdMixin(object):
    id = Column(INTEGER, primary_key=True, autoincrement=True)


class UuidMixin(object):
    uuid = Column(VARCHAR(36), nullable=False, default=func.uuid())


class StatusMixin(object):
    status = Column(TINYINT, nullable=False, default=1, comment='记录状态：1 - 正常')


# class BaseModelMixin(object):
class BaseModelMixin(IdMixin, UuidMixin, TimestampMixin, StatusMixin):
    __comment__ = None

    # id = Column(INTEGER, primary_key=True, autoincrement=True)
    # uuid = Column(VARCHAR(36), nullable=False, default=str(uuid.uuid4()))
    # created_at = Column(DATETIME, nullable=False, default=func.now(), server_default=func.now())
    # updated_at = Column(DATETIME, nullable=False, default=func.now(), server_default=func.now(), onupdate=func.now())
    # status = Column(TINYINT, nullable=False, default=1, comment='记录状态：1 - 正常')

    def __init__(self, *args, **kwargs):
        pass

    @declared_attr
    def __table_args__(cls):
        table_args = {'mysql_engine': 'InnoDB'}
        if cls.__comment__ is not None:
            table_args['comment'] = cls.__comment__
        return table_args

    def to_dict(self, *exclude_columns):
        """
        convert model to dict, ignore id column as default.

        :param exclude_columns:
        :return:
        """
        if len(exclude_columns) == 0:
            exclude_columns = ('id',)
        else:
            ['id'].extend(exclude_columns)

        data = {}
        for column in self.__table__.columns:
            if column.name in exclude_columns:
                continue

            row = getattr(self, column.name, '')

            if isinstance(row, datetime):
                # row = row.strftime('%Y-%m-%d %H:%M:%S')
                row = row.isoformat()
            if isinstance(row, Decimal):
                row = float(row)

            data[column.name] = row
        return data

    def to_json_string(self):
        data = {}
        for column in self.__table__.columns:
            row = getattr(self, column.name, '')
            if isinstance(row, datetime):
                row = row.strftime('%Y-%m-%d %H:%M:%S')
            data[column.name] = row
        return json.dumps(data)

    @classmethod
    def from_json_string(cls, json_string: str):
        data = json.loads(json_string)  # type:dict
        model = cls(**data)
        for key, value in data.items():
            setattr(model, key, value)
        return model


# Base = declarative_base(cls=BaseModel)
Base = declarative_base()
