# -*- coding: utf-8 -*-
from enum import Enum

from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import VARCHAR

from application.model.base_model import Base, BaseModelMixin


class Event(Base, BaseModelMixin):
    __tablename__ = 'event'
    __comment__ = '公告'

    author_uuid = Column(VARCHAR(36))
    title = Column(VARCHAR(128))
    summary = Column(String)
    content = Column(String)

    __immutable_columns__ = ['id', 'author_uuid', 'created_at']
    __required_columns_for_creation__ = ['author_uuid', 'title', 'summary', 'content']
    __allow_columns_for_creation__ = ['status']

    class Status(Enum):
        # 状态：0 - 初始化，1 - 有效，2 - 作废
        INITIALIZATION = 0
        VALID = 1
        DELETED = 2

    def __init__(self, *args, author_uuid=None, title=None, summary=None, content=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.author_uuid = author_uuid
        self.title = title
        self.summary = summary
        self.content = content


cacheable = Event
