#!/usr/bin/python3
# -*-coding:utf-8 -*-
import time

from sqlalchemy import Table, Column, Integer, String, Date, Float, Boolean, LargeBinary, DATETIME, BIGINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def to_dict(model):
    return {c.name: getattr(model, c.name) for c in model.__table__.columns}


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    password = Column(String)
    name = Column(String)
    image = Column(String)
    created_at = Column(Float)
    last_login_at = Column(Float)
    available = Column(Boolean)
    total_usage = Column(Integer)

    def __init__(self, username=None, email=None, password=None, name=None, image=None, admin=False, created_at=None,
                 last_login_at=None, available=True):
        self.username = username
        self.email = email
        self.password = password
        self.name = name
        self.image = image
        self.admin = admin
        self.created_at = created_at if created_at else time.time()
        self.last_login_at = last_login_at if last_login_at else time.time()
        self.available = available
        self.total_usage = 0

    def __repr__(self):
        return '<User %s: %s>' % (self.username, self.email)


class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    label = Column(String)
    description = Column(String)

    def __init__(self, name, label, description=None):
        self.name = name
        self.label = label
        self.description = description

    def __repr__(self):
        return '<Role %s: %s>' % (self.name, self.description)

    # role_id list
    # 超级管理员, root
    ROOT = 1
    # 注册用户, user
    USER = 2
    # 小黑屋，ban
    BAN = 3


class UserRole(Base):
    __tablename__ = 'user_role'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    role_id = Column(Integer)

    def __init__(self, user_id, role_id):
        self.user_id = user_id
        self.role_id = role_id

    def __repr__(self):
        return '<UserRole %s: user_id = %s, role_id = %s>' % (self.id, self.user_id, self.role_id)


class Permission(Base):
    __tablename__ = 'permission'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    label = Column(String)
    description = Column(String)

    def __init__(self, name, label, description=None):
        self.name = name
        self.label = label
        self.description = description

    def __repr__(self):
        return '<Permission %s(%s): %s>' % (self.name, self.label, self.description)

    # permission_id list
    # 登录，login
    LOGIN = 1
    # 后台管理，manage
    MANAGE = 2
    # 邀请码管理，manage_invitation_code
    MANAGE_INVITATION_CODE = 3
    # 公告管理, manage_event
    MANAGE_EVENT = 4
    # 用户管理，manage_user
    MANAGE_USER = 5
    # 角色管理，manage_role
    MANAGE_ROLE = 6
    # 套餐模板管理 manage_service_template
    MANAGE_SERVICE_TEMPLATE = 7
    # 用户学术积分管理
    MANAGE_SCHOLAR_BALANCE = 8
    # 用户套餐管理
    MANAGE_SERVICE = 9


class RolePermission(Base):
    __tablename__ = 'role_permission'

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer)
    permission_id = Column(Integer)

    def __init__(self, role_id, permission_id):
        self.role_id = role_id
        self.permission_id = permission_id


class InvitationCode(Base):
    __tablename__ = 'invitation_code'

    id = Column(Integer, primary_key=True)
    code = Column(String)
    inviter_id = Column(Integer)
    invitee_id = Column(Integer)
    available = Column(Boolean)
    created_at = Column(Float)
    invited_at = Column(Float)

    def __init__(self, code, inviter_id, invitee_id=None, available=None, created_at=None,
                 invited_at=None):
        self.code = code
        self.inviter_id = inviter_id
        self.invitee_id = invitee_id
        self.available = available if available else True
        self.created_at = created_at if created_at else time.time()
        self.invited_at = invited_at

    def __repr__(self):
        return '<InvitationCode %s %s %s>' % (self.id, self.code, self.available)


class Event(Base):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    name = Column(String)
    tag = Column(String)
    summary = Column(String)
    content = Column(String)
    created_at = Column(Float)
    available = Column(Boolean)

    def __init__(self, user_id=None, name=None, tag=None, summary=None, content=None, created_at=None,
                 available=True):
        self.user_id = user_id
        self.name = name
        self.tag = tag
        self.summary = summary
        self.content = content
        self.created_at = created_at if created_at else time.time()
        self.available = available

    def __repr__(self):
        return '<Event %s %s>' % (self.name, self.tag)


class ServiceTemplate(Base):
    __tablename__ = 'service_template'

    id = Column(Integer, primary_key=True)
    type = Column(Integer)
    title = Column(String)
    subtitle = Column(String)
    description = Column(String)
    balance = Column(BIGINT)
    price = Column(Integer)
    initialization_fee = Column(Integer)

    def __init__(self, type=None, title=None, subtitle=None, description=None, balance=None, price=None,
                 initialization_fee=None):
        self.type = type
        self.title = title
        self.subtitle = subtitle
        self.description = description
        self.balance = balance
        self.price = price
        self.initialization_fee = initialization_fee

    def __repr__(self):
        return '<ServiceTemplate %s %s>' % (self.title, self.balance)

    # 包月套餐
    MONTHLY = 0
    # 流量套餐
    DATA = 1


class Service(Base):
    __tablename__ = 'service'

    id = Column(Integer, primary_key=True)
    usage = Column(BIGINT)
    package = Column(BIGINT)
    auto_renew = Column(Boolean)
    reset_at = Column(Float)
    last_reset_at = Column(Float)
    created_at = Column(Float)
    expired_at = Column(Float)
    total_usage = Column(BIGINT)
    template_id = Column(Integer)
    available = Column(Boolean)
    alive = Column(Boolean)

    def __init__(self, usage=None, package=None, auto_renew=None, reset_at=None, last_reset_at=None, created_at=None,
                 expired_at=None,
                 total_usage=None, template_id=None, available=True, alive=True):
        self.usage = usage
        self.package = package
        self.auto_renew = auto_renew
        self.reset_at = reset_at
        self.last_reset_at = last_reset_at
        self.created_at = created_at if created_at else time.time()
        self.expired_at = expired_at
        self.total_usage = total_usage
        self.template_id = template_id
        self.available = available
        self.alive = alive

    def __repr__(self):
        return '<Service %s %s>' % (self.usage, self.package)


class ServicePassword(Base):
    __tablename__ = 'service_password'

    id = Column(Integer, primary_key=True)
    service_id = Column(Integer)
    port = Column(Integer)
    password = Column(String)

    def __init__(self, service_id=None, port=None, password=None):
        self.service_id = service_id
        self.port = port
        self.password = password

    def __repr__(self):
        return '<ServicePassword %s %s>' % (self.port, self.password)


class UserService(Base):
    __tablename__ = 'user_service'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    service_id = Column(Integer)

    def __init__(self, user_id=None, service_id=None):
        self.user_id = user_id
        self.service_id = service_id

    def __repr__(self):
        return '<UserService %s %s>' % (self.user_id, self.service_id)


class UserScholarBalance(Base):
    __tablename__ = 'user_scholar_balance'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    balance = Column(Integer)

    def __init__(self, user_id=None, balance=None):
        self.user_id = user_id
        self.balance = balance

    def __repr__(self):
        return '<UserScholarBalance %s %s>' % (self.user_id, self.balance)
