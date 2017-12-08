#!/usr/bin/python3
# -*-coding:utf-8 -*-

import datetime

import jinja2
import time
# import qiniu


# def init_qiniu(app):
#     access_key = app.config['QINIU_ACCESS_KEY']
#     secret_key = app.config['QINIU_SECRET_KEY']
#     q = qiniu.Auth(access_key, secret_key)
#
#     return q
from flask_sqlalchemy import SQLAlchemy

import database
from view import method_views, views


def init_jinja2_global(app):
    app.add_template_global(app.config['URL_OF_STATIC'], 'static_route')
    app.add_template_global(app.config['DEBUG'], 'debug')
    # 防止VUE和Jinja2冲突
    app.jinja_env.variable_start_string = '{{ '
    app.jinja_env.variable_end_string = ' }}'


def init_jinja2():
    jinja2.filters.FILTERS['comment_datetime'] = datetime_filter
    jinja2.filters.FILTERS['datetime'] = datetime_filter2
    jinja2.filters.FILTERS['boolean_to_yes'] = boolean_to_yes_or_no
    jinja2.filters.FILTERS['service_type'] = service_type_to_str


def init_method_views(app):
    method_views.init_app(app)


def init_views(app):
    views.init_app(app)


def init_database(app):
    database.set_sqlalchemy_database_uri(app.config['SQLALCHEMY_DATABASE_URI'])
    database.set_db_with_pagination(SQLAlchemy(app))


def datetime_filter(t):
    if t is None:
        return t

    delta = int(time.time() - t)
    if delta < 60:
        return u'1分钟前'
    if delta < 3600:
        return u'%s分钟前' % (delta // 60)
    if delta < 86400:
        return u'%s小时前' % (delta // 3600)
    if delta < 604800:
        return u'%s天前' % (delta // 86400)
    if delta < 2592000:
        return u'%s天前' % (delta // 86400)

    return datetime_filter2(t)


def datetime_filter2(t):
    if t is None:
        return t

    dt = datetime.datetime.fromtimestamp(t)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def boolean_to_yes_or_no(boolean):
    if boolean:
        return 'YES'
    else:
        return 'NO'


def service_type_to_str(service_type):
    if service_type == 0:
        return '包月套餐'
    elif service_type == 1:
        return '流量套餐'
    else:
        return '未知类型'

