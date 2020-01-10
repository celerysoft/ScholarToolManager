#!/usr/bin/python3
# -*-coding:utf-8 -*-

from flask import session

from application.model.legacy import model
import application.exception.http
from application.model.permission import Permission
from application.model.role import Role
from application.model.role_permission import RolePermission
from application.model.user import User
from application.model.user_role import UserRole


def check_user_api_permission():
    """
    查询用户是否已经登录
    :return:
    """
    if 'user' not in session.keys():
        raise application.exception.api.Unauthorized('该接口只允许已登录用户调用')


def check_user_permission():
    """
    查询用户是否已经登录
    :return:
    """
    if 'user' not in session.keys():
        raise application.exception.http.Unauthorized('请先登录')


def derive_user_permissions(db_session, user_id):
    """
    查询用户权限
    :param db_session: sqlalchemy
    :param user_id: 用户id
    :return: 用户的权限
    """
    permissions = db_session.query(model.Permission) \
        .filter(model.User.id == model.UserRole.user_id) \
        .filter(model.UserRole.role_id == model.Role.id) \
        .filter(model.Role.id == model.RolePermission.role_id) \
        .filter(model.RolePermission.permission_id == model.Permission.id) \
        .filter(model.User.id == user_id).all()

    # print(permissions)
    # for p in permissions:
    #     print(p)

    return permissions


def check_permission(db_session, user_id, permission_id):
    permissions = derive_user_permissions(db_session, user_id)
    # print(permissions)
    for permission in permissions:
        if permission.id == permission_id:
            return True

    return False


def check_login_permission(db_session, user_id):
    return check_permission(db_session, user_id, model.Permission.LOGIN)


def check_manage_permission(db_session, user_id):
    return check_permission(db_session, user_id, model.Permission.MANAGE)


def check_manage_permission_permission(db_session, user_id):
    return check_permission(db_session, user_id, model.Permission.MANAGE_PERMISSION)


def check_manage_event_permission(db_session, user_id):
    return check_permission(db_session, user_id, model.Permission.MANAGE_EVENT)


def check_manage_user_permission(db_session, user_id):
    return check_permission(db_session, user_id, model.Permission.MANAGE_USER)


def check_manage_role_permission(db_session, user_id, call_by_api=False):
    if call_by_api:
        check_user_api_permission()

    return check_permission(db_session, user_id, model.Permission.MANAGE_ROLE)


def check_manage_invitation_code_permission(db_session, user_id, call_by_api=False):
    if call_by_api:
        check_user_api_permission()

    return check_permission(db_session, user_id, model.Permission.MANAGE_INVITATION_CODE)


def check_manage_service_template_permission(db_session, user_id, call_by_api=False):
    if call_by_api:
        check_user_api_permission()

    return check_permission(db_session, user_id, model.Permission.MANAGE_SERVICE_TEMPLATE)


def check_manage_scholar_balance_permission(db_session, user_id, call_by_api=False):
    if call_by_api:
        check_user_api_permission()

    return check_permission(db_session, user_id, model.Permission.MANAGE_SCHOLAR_BALANCE)


def check_manage_service_permission(db_session, user_id, call_by_api=False):
    if call_by_api:
        check_user_api_permission()

    return check_permission(db_session, user_id, model.Permission.MANAGE_SERVICE)


class PermissionToolkit(object):
    @staticmethod
    def derive_user_permissions(db_session, user_uuid):
        """
        查询用户权限
        :param db_session: sqlalchemy
        :param user_uuid: 用户uuid
        :return: 用户的权限
        """
        permissions = db_session.query(Permission) \
            .filter(User.uuid == UserRole.user_uuid) \
            .filter(UserRole.role_uuid == Role.uuid) \
            .filter(Role.uuid == RolePermission.role_uuid) \
            .filter(RolePermission.permission_uuid == Permission.uuid) \
            .filter(User.uuid == user_uuid).all()

        return permissions

    @classmethod
    def _check_permission_by_permission_uuid(cls, db_session, user_uuid, permission_uuid) -> bool:
        permission = db_session.query(Permission) \
            .filter(User.uuid == UserRole.user_uuid) \
            .filter(UserRole.role_uuid == Role.uuid) \
            .filter(Role.uuid == RolePermission.role_uuid) \
            .filter(RolePermission.permission_uuid == Permission.uuid) \
            .filter(User.uuid == user_uuid) \
            .filter(Permission.uuid == permission_uuid) \
            .first()
        return permission is not None

    @classmethod
    def _check_permission_by_permission_label(cls, db_session, user_uuid, label: Permission.PermissionLabel) -> bool:
        permission = db_session.query(Permission) \
            .filter(User.uuid == UserRole.user_uuid) \
            .filter(UserRole.role_uuid == Role.uuid) \
            .filter(Role.uuid == RolePermission.role_uuid) \
            .filter(RolePermission.permission_uuid == Permission.uuid) \
            .filter(User.uuid == user_uuid) \
            .filter(Permission.label == label.value) \
            .first()
        return permission is not None

    def _check_permission(self, session, user_uuid, permission_required):
        return False

    def check_manage_permission(self, session, user_uuid):
        return self._check_permission_by_permission_label(session, user_uuid, Permission.PermissionLabel.MANAGEMENT)

    def check_login_permission(self, db_session, user_id) -> bool:
        return self._check_permission(db_session, user_id, model.Permission.LOGIN)

    def check_manage_event_permission(self, db_session, user_id) -> bool:
        return self._check_permission(db_session, user_id, model.Permission.MANAGE_EVENT)

    def check_manage_scholar_balance_permission(self, db_session, user_id) -> bool:
        return self._check_permission(db_session, user_id, model.Permission.MANAGE_SCHOLAR_BALANCE)

    def check_manage_role_permission(self, db_session, user_id) -> bool:
        return self._check_permission(db_session, user_id, model.Permission.MANAGE_ROLE)

    def check_manage_invitation_code_permission(self, db_session, user_id) -> bool:
        return self._check_permission(db_session, user_id, model.Permission.MANAGE_INVITATION_CODE)

    def check_manage_service_template_permission(self, db_session, user_id) -> bool:
        return self._check_permission(db_session, user_id, model.Permission.MANAGE_SERVICE_TEMPLATE)


toolkit = PermissionToolkit()
