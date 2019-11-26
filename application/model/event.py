# -*- coding: utf-8 -*-
from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import VARCHAR

from application.model.base_model import Base, BaseModelMixin


class Event(Base, BaseModelMixin):
    __tablename__ = 'event'
    __comment__ = '公告'
    __immutable_columns__ = ['id', 'user_id', 'created_at']

    author_uuid = Column(VARCHAR(36))
    title = Column(VARCHAR(128))
    summary = Column(String)
    content = Column(String)

    def __init__(self, author_uuid=None, title=None, summary=None, content=None):
        super().__init__()

        self.author_uuid = author_uuid
        self.title = title
        self.summary = summary
        self.content = content


cacheable = Event
