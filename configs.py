#!/usr/bin/python3
# -*-coding:utf-8 -*-
import os

# 是否开启DEBUG模式
DEBUG = True
# 是否开启TESTING模式
TEST = True

# 数据库相关
LEGACY_DB_HOST = '127.0.0.1'
LEGACY_DB_PORT = '3306'
LEGACY_DB_USER = 'www-data'
LEGACY_DB_PASSWORD = 'www->R&daD6xZM6283n3-data'
LEGACY_DB_NAME = 'scholar_tool_manager'

DB_HOST = '127.0.0.'
DB_PORT = '3306'
DB_USER = 'www-data'
DB_PASSWORD = 'www->R&daD6xZM6283n3-data'
DB_NAME = 'scholar_tool'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BASE_URL = '/api'

# Write api exception to log file
BUILD_API_EXCEPTION = False

# JSON显示中文
JSON_AS_ASCII = False
# session的secret
SECRET_KEY = 'scholar.celerysoft.com'
# 加密密码时的盐
SHA1_SALT = 'whosyourdaddy'
# 新版密码的盐
PASSWORD_SALT = 'whosyourdaddy'
JWT_SECRET = 'whosyourdaddy'
# 分页时每页的项目数
ITEM_PER_PAGE = 10
# session的域名
# SESSION_COOKIE_DOMAIN = 'celerysoft.science'
# session类型 http://pythonhosted.org/Flask-Session/
SESSION_TYPE = 'sqlalchemy'
SESSION_USE_SIGNER = True
# 数据库的URI
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' \
                          % (LEGACY_DB_USER, LEGACY_DB_PASSWORD, LEGACY_DB_HOST, LEGACY_DB_PORT, LEGACY_DB_NAME)
SQLALCHEMY_TRACK_MODIFICATIONS = True

# 手动生成以hash版本命名的静态资源文件的目录
CDN_STATIC_ROOT = '/Users/admin/Developer/Python/scholar-tool-manager/local/cdn'
# 静态资源基于文件内容的hash版本冗余机制，会将自动生成后的文件放到该目录下
STATIC_ROOT = '/Users/admin/Developer/Python/scholar-tool-manager/local/static'
# static目录的路径，测试时为本地，上线时为cdn
URL_OF_STATIC = ''
# 博客图片的路径
URL_OF_BLOG_IMAGE = '/static/image/blog/'
# 匿名评论用户的用户名（username）字段
ANONYMOUS_USER_NAME = 'anonymous'
# 七牛access_key
QINIU_ACCESS_KEY = 'YCHyZnl8DPE2T107dsYcLnSbb1rQZb1igf-tdiRm'
# 七牛secret_key
QINIU_SECRET_KEY = '9BiplXuagdDwocKpjiWEAfDhTh68iSM82_6OyIdq'
# 上传头像到七牛时七牛空间名
QINIU_BUCKET_NAME = 'celerysoft-science'
# 上传头像到七牛时图片名前缀
URL_OF_AVATAR_IMAGE = 'static/image/avatar/'
# 上传头像到七牛时图片的外链默认域名
URL_OF_QINIU_AVATAR = 'http://oz3d04vwf.bkt.clouddn.com/'
# 数据库备份文件上传到七牛时的空间名
QINIU_BUCKET_NAME_FOR_BACKUP_DATABASE = 'database'
# 数据库备份文件本地存放目录
DATABASE_BACKUP_FILE_DIRECTORY = '/Users/admin/Documents/'
# 新注册用户默认学术积分
NEW_USER_SCHOLAR_BALANCE = 5120
# reCAPTCHA secret key
RE_CAPTCHA_SECRET_KEY = '6LenHTkUAAAAACSATcazsqs3kuH6NkT7KQMz4-dvdcps'
# 日志文件
LOG_FILE = '/Users/admin/Developer/Python/scholar-tool-manager/local/app.log'
# SS服务监听器重启脚本地址
SS_LISTENER_RESTART_SHELL_FILE_PATH = '/Users/admin/Developer/Script/restart_ss_listener.sh'
# SS服务监听器日志文件
SS_LISTENER_LOG_FILE = '/Users/admin/Developer/Python/scholar-tool-manager/local/ss-listener.log'
# SS服务起始端口号
SERVICE_MIN_PORT = 20001
# SS服务配置文件路径
SHADOWSOCKS_CONFIG_FILE_PATH = \
    '/Users/admin/Developer/Python/scholar-tool-manager/local/multiple_users_config.json'
# 主服务器地址，数据库，网页所在的服务器地址
MAIN_SERVER_ADDRESS = 'http://127.0.0.1:20000'
# SS服务unix domain socket的地址
SS_SERVER_UDS_ADDRESS = '/Users/admin/Developer/Python/scholar-tool-manager/local/shadowsocks-manage.sock'
# ss_controller的unix domain socket的地址
SS_CONTROLLER_UDS_CLIEND_ADDRESS = \
    '/Users/admin/Developer/Python/scholar-tool-manager/local/shadowsocks-controller-client.sock'
# ss_listener的unix domain socket的地址
SS_LISTENER_UDS_CLIEND_ADDRESS = \
    '/Users/admin/Developer/Python/scholar-tool-manager/local/shadowsocks-listener-client.sock'
# ss_listener上报流量使用情况的频率（秒）
SS_LISTENER_WORKING_FREQUENCY = 30

# ss 客户端名称
SS_CLIENT = 'shadowsocks-libev'

# Celery stuffs
CELERY_BROKER_URL = 'redis://localhost:6379/10'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/10'

# 学术积分账户支付系统Celery配置
SCHOLAR_PAYMENT_SYSTEM_CELERY_BROKER_URL = 'redis://localhost:6379/8'
SCHOLAR_PAYMENT_SYSTEM_CELERY_RESULT_BACKEND = 'redis://localhost:6379/8'

# 学术积分账户系统配置
# app_id 及 app_secret
SCHOLAR_PAYMENT_SYSTEM_UUID_IN_PAYMENT_METHOD = ''
SCHOLAR_PAYMENT_SYSTEM_APP_ID = '0001'
SCHOLAR_PAYMENT_SYSTEM_APP_SECRET = ''


# Redis for Cache System
REDIS_HOST = 'localhost'
REDIS_PORT = '6379'
REDIS_DB = '0'

# 邮件服务
SMTP_PASSWORD = ''


try:
    from local_settings import *
except ImportError:
    pass
