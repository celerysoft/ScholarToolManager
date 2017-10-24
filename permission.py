from flask import session

import model
import exception.http
import exception.api


def check_user_api_permission():
    if 'user' not in session.keys():
        raise exception.api.Unauthorized('该接口只允许已登录用户调用')


def check_user_permission():
    if 'user' not in session.keys():
        raise exception.http.Unauthorized('请先登录')


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
    print(user_id)
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
