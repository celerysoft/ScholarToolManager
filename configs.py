#!/usr/bin/python3
# -*-coding:utf-8 -*-


class Config(object):
    # 数据库相关
    _db_host = '127.0.0.1'
    _db_port = '3306'
    _db_user = 'www-data'
    _db_password = 'www->R&daD6xZM6283n3-data'
    _db_name = 'scholar_tool_manager'

    # 是否开启DEBUG模式
    DEBUG = False
    # 是否开启TESTING模式
    TESTING = False
    # JSON显示中文
    JSON_AS_ASCII = False
    # session的secret
    SECRET_KEY = 'scholar.celerysoft.com'
    # 加密密码时的盐
    SHA1_SALT = 'whosyourdaddy'
    # 分页时每页的项目数
    ITEM_PER_PAGE = 10
    # 本地测试时的HOST
    HOST = '127.0.0.1'
    # 本地测试时的端口
    PORT = 50001
    # session类型 http://pythonhosted.org/Flask-Session/
    SESSION_TYPE = 'sqlalchemy'
    SESSION_USE_SIGNER = True
    # 数据库的URI
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://' \
                              + _db_user + ':' + _db_password + '@' + _db_host + ':' + _db_port + '/' + _db_name
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # static目录的路径，测试时为本地，上线时为cdn
    URL_OF_STATIC = ''
    # 博客图片的路径
    URL_OF_BLOG_IMAGE = '/static/image/blog/'
    # 匿名评论用户的用户名（username）字段
    ANONYMOUS_USER_NAME = 'anonymous'
    # 上传头像到七牛时七牛空间名
    QINIU_BUCKET_NAME = 'celerysoft-com'
    # 上传头像到七牛时图片名前缀
    URL_OF_AVATAR_IMAGE = 'static/image/avatar/'
    # 上传头像到七牛时图片的外链默认域名
    URL_OF_QINIU_AVATAR = 'http://ow92gcjek.bkt.clouddn.com/'


class DevelopmentConfig(Config):
    """
    开发环境
    """
    _db_name = 'scholar_tool_manager_test'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://' + Config._db_user + ':' + Config._db_password \
                              + '@' + Config._db_host + ':' + Config._db_port + '/' + _db_name
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class TestingConfig(Config):
    """
    测试环境
    """
    TESTING = True


class ProductionConfig(Config):
    """
    生产环境
    """
    URL_OF_STATIC = 'http://ow92gcjek.bkt.clouddn.com'
    URL_OF_BLOG_IMAGE = 'http://ow92gcjek.bkt.clouddn.com/static/image/blog/'
