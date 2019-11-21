# -*- coding: utf-8 -*-
from flask import make_response, Blueprint

from app import derive_import_root, add_url_rules_for_blueprint
from application import exception
from application.model.model import User, Role, UserRole, to_dict, RolePermission
from application.util import permission
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


class RoleAPI(BaseNeedLoginAPI):
    methods = ['GET', 'POST', 'PATCH', 'DELETE']

    def get(self):
        with session_scope() as db_session:
            if not permission.check_manage_role_permission(db_session, self.user_id):
                raise exception.api.Forbidden('当前用户无法管理角色')

            # 查询用户当前角色
            user_role = None
            target_user_id = self.get_data('user_id')
            if self.valid_data(target_user_id):
                user_role = db_session.query(Role) \
                    .filter(User.id == UserRole.user_id) \
                    .filter(UserRole.role_id == Role.id) \
                    .filter(User.id == target_user_id).first()

            # 查询所有角色列表
            roles = db_session.query(Role).order_by(Role.id).all()

            role_list = []
            for role in roles:
                role_list.append(to_dict(role))

            payload = {
                'roles': role_list
            }
            if user_role is not None:
                payload['user_role'] = to_dict(user_role)

        result = ApiResult('获取角色信息成功', 200, payload)
        return make_response(result.to_response())

    def post(self):
        name = self.get_post_data('name', require=True, error_message='缺少name字段')
        label = self.get_post_data('label', require=True, error_message='缺少label字段')
        description = self.get_post_data('description')
        permissions = self.get_post_data('permissions')

        with session_scope() as session:
            if not permission.toolkit.check_manage_role_permission(session, self.user_id):
                raise exception.api.Forbidden('当前用户无法管理角色')

            role = Role(name, label, description)
            session.add(role)
            session.flush()

            role_id = role.id
            for permission_id in permissions:
                role_permission = RolePermission(role_id, permission_id)
                session.add(role_permission)

        result = ApiResult('创建角色成功', 201, {
            'role_id': role_id
        })
        return make_response(result.to_response())

    def patch(self):
        role_id = self.get_post_data('id', require=True, error_message='缺少id字段')
        name = self.get_post_data('name', require=True, error_message='缺少name字段')
        label = self.get_post_data('label', require=True, error_message='缺少label字段')
        description = self.get_post_data('description')
        permissions = self.get_post_data('permissions')

        with session_scope() as session:
            if not permission.toolkit.check_manage_role_permission(session, self.user_id):
                raise exception.api.Forbidden('当前用户无法管理角色')

            # 更新role表
            role = session.query(Role).filter(Role.id == role_id).first()
            if role is None:
                raise exception.api.NotFound('角色不存在')

            role.name = name
            role.label = label
            role.description = description

            # 删除role_permission表的旧记录
            # TODO 软删除
            role_permissions = session.query(RolePermission) \
                .filter(Role.id == RolePermission.role_id) \
                .filter(Role.id == role_id).all()

            for role_permission in role_permissions:
                session.delete(role_permission)

            # 新增角色权限记录到role_permission表
            for permission_id in permissions:
                role_permission = RolePermission(role_id, permission_id)
                session.add(role_permission)

        result = ApiResult('更新角色成功', 201, {
            'role_id': role_id
        })
        return make_response(result.to_response())

    def delete(self):
        # TODO 软删除
        role_id = self.get_data('id')
        if not self.valid_data(role_id):
            role_id = self.get_post_data('id', require=True, error_message='所需删除的角色id不能为空')

        with session_scope() as session:

            if not permission.toolkit.check_manage_role_permission(session, self.user_id):
                raise exception.api.Forbidden('当前用户无法管理角色')

            # 判断是否有user的角色是待删除角色
            users = session.query(User) \
                .filter(UserRole.user_id == User.id) \
                .filter(UserRole.role_id == Role.id) \
                .filter(Role.id == role_id).all()

            if users is not None and len(users) > 0:
                raise exception.api.InvalidRequest('当前还有{}位用户的角色为待删除角色，故无法删除该角色'.format(users))

            # 从role表删除记录
            role = session.query(Role).filter_by(id=role_id).first()
            if role is None:
                raise exception.api.NotFound('需要删除的角色不存在')
            session.delete(role)

            # 从role_permission表删除记录
            role_permissions = session.query(RolePermission) \
                .filter(Role.id == role_id) \
                .filter(Role.id == RolePermission.role_id).all()
            for role_permission in role_permissions:
                session.delete(role_permission)

        result = ApiResult('删除角色成功')
        return make_response(result.to_response())


view = RoleAPI

bp = Blueprint(__name__.split('.')[-1], __name__)
root = derive_import_root(__name__)
add_url_rules_for_blueprint(root, bp)
