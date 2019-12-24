# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, create_engine
from sqlalchemy.dialects.mysql import VARCHAR, TINYINT, DATE
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.util.compat import contextmanager

import configs
from application.util.cache import cache
from application.views.base_api import BaseNeedLoginAPI, ApiResult


uri = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' \
          % (configs.TENCENT_NEWS_DB_USER, configs.TENCENT_NEWS_DB_PASSWORD, configs.TENCENT_NEWS_DB_HOST,
             configs.TENCENT_NEWS_DB_PORT, configs.TENCENT_NEWS_DB_NAME)
engine = create_engine(uri, pool_recycle=3600)
Session = sessionmaker(bind=engine)


@contextmanager
def session_scope():
    global Session
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


Base = declarative_base()


class TencentNewsCrawling(Base):
    __tablename__ = 'tencent_news_crawling'

    id = Column(Integer, primary_key=True)
    title = Column(VARCHAR)
    view_count = Column(Integer)
    comment_count = Column(Integer)
    publish_date = Column(DATE)
    url_for_desktop = Column(VARCHAR)
    status = Column(TINYINT)


class YesterdayNewsAPI(BaseNeedLoginAPI):
    methods = ['GET']

    def get(self):
        cache_key = 'api-yesterday-news-{}'.format(datetime.now().strftime('%Y-%m-%d'))
        yesterday_news_json_str = cache.get(cache_key)
        if not self.valid_data(yesterday_news_json_str):
            with session_scope() as session:
                news_list = []
                yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                news = session.query(TencentNewsCrawling) \
                    .filter(TencentNewsCrawling.publish_date == yesterday,
                            TencentNewsCrawling.status == 1) \
                    .order_by(TencentNewsCrawling.view_count.desc()).all()
                for item in news:  # type: TencentNewsCrawling
                    news_list.append({
                        'id': item.id,
                        'title': item.title,
                        'view_count': item.view_count,
                        'comment_count': item.comment_count,
                        'publish_date': item.publish_date.isoformat(),
                        'url_for_desktop': item.url_for_desktop,
                        'status': item.status
                    })
                payload = {
                    'news': news_list,
                }
                yesterday_news_json_str = json.dumps(payload)
                cache.set(cache_key, yesterday_news_json_str)
        else:
            payload = json.loads(yesterday_news_json_str)

        result = ApiResult('获取昨日要闻数据成功', payload=payload)
        return result.to_response()


view = YesterdayNewsAPI
