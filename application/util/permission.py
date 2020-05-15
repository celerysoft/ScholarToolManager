#!/usr/bin/python3
# -*-coding:utf-8 -*-

from application.model.permission import Permission
from application.model.role import Role
from application.model.role_permission import RolePermission
from application.model.user import User
from application.model.user_role import UserRole


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
            .filter(User.uuid == user_uuid) \
            .filter(~User.status.in_([User.STATUS.SUSPENDED, User.STATUS.DELETED]),
                    UserRole.status == UserRole.Status.VALID.value,
                    RolePermission.status == RolePermission.Status.VALID.value) \
            .all()

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
            .filter(~User.status.in_([User.STATUS.SUSPENDED, User.STATUS.DELETED]),
                    UserRole.status == UserRole.Status.VALID.value,
                    RolePermission.status == RolePermission.Status.VALID.value) \
            .first()
        return permission is not None

    @classmethod
    def _check_permission_by_built_in_permission(cls, db_session, user_uuid,
                                                 build_in_permission: Permission.BuiltInPermission) -> bool:
        permission = db_session.query(Permission).select_from(User).outerjoin(
            UserRole, UserRole.user_uuid == User.uuid).outerjoin(
            Role, Role.uuid == UserRole.role_uuid).outerjoin(
            RolePermission, RolePermission.role_uuid == Role.uuid).outerjoin(
            Permission, Permission.uuid == RolePermission.permission_uuid).filter(
            User.uuid == user_uuid,
            Permission.label == build_in_permission.value.label,
            ~User.status.in_([User.STATUS.SUSPENDED, User.STATUS.DELETED]),
            UserRole.status == UserRole.Status.VALID.value,
            RolePermission.status == RolePermission.Status.VALID.value).first()
        return permission is not None

    def _check_permission(self, session, user_uuid, permission_required):
        return False

    def check_manage_permission(self, db_session, user_uuid):
        return self._check_permission_by_built_in_permission(db_session, user_uuid,
                                                             Permission.BuiltInPermission.MANAGEMENT)

    def check_login_permission(self, db_session, user_uuid) -> bool:
        return self._check_permission_by_built_in_permission(db_session, user_uuid,
                                                             Permission.BuiltInPermission.LOGIN)

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
