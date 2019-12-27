# -*- coding: utf-8 -*-
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

    def __init__(self, *args, author_uuid=None, title=None, summary=None, content=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.author_uuid = author_uuid
        self.title = title
        self.summary = summary
        self.content = content


cacheable = Event
