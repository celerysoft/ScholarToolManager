# -*-coding:utf-8 -*-
"""

"""
import os
import shutil

from application.model.event import Event
from application.model.payment_method import PaymentMethod
from application.model.permission import Permission
from application.model.role import Role
from application.model.role_permission import RolePermission
from application.model.scholar_payment_account import ScholarPaymentAccount
from application.model.service_template import ServiceTemplate
from application.model.user import User
from application.model.user_role import UserRole
from application.util import authorization
from application.util.database import session_scope


class ProjectInitializationToolkit(object):
    def create_config_file(self) -> bool:
        try:
            if os.path.exists('local_settings.py'):
                os.rename('local_settings.py', 'local_settings.py.bak')
            shutil.copyfile('application/config/local_settings', 'local_settings.py')
            if not os.path.exists('local_settings.py'):
                return False
        except:
            return False
        return True

    def execute(self) -> bool:
        with session_scope() as session:
            try:
                self._create_built_in_permissions(session)
                self._create_built_in_role(session)
                self._assign_role_permission(session)
                self._create_built_in_user(session)
                self._assign_role_for_built_in_user(session)
                self._create_scholar_account_for_built_in_user(session)
                self._create_default_event(session)
                self._create_default_service_template(session)
                self._create_built_in_payment_method(session)
                session.commit()
            except:
                return False
            return True

    @staticmethod
    def _create_built_in_permissions(session):
        for built_in_permission_enum in Permission.BuiltInPermission:
            built_in_permission = built_in_permission_enum.value
            permission = Permission(
                name=built_in_permission.name,
                label=built_in_permission.label,
                description=built_in_permission.description,
            )
            session.add(permission)
        session.flush()
        # session.commit()

    @staticmethod
    def _create_built_in_role(session):
        for built_in_permission_enum in Role.BuiltInRole:
            built_in_role = built_in_permission_enum.value  # type: Role.BuiltInRole.BuiltInRoleObject
            role = Role(
                name=built_in_role.name,
                description=built_in_role.description,
            )
            session.add(role)
        # session.commit()
        session.flush()

    @classmethod
    def _assign_role_permission(cls, session):
        cls._assign_permission_to_role(session, Role.BuiltInRole.REGISTRATION_USER, Permission.BuiltInPermission.LOGIN)

        cls._assign_permission_to_role(session, Role.BuiltInRole.ADMINISTRATOR,
                                       Permission.BuiltInPermission.LOGIN, Permission.BuiltInPermission.MANAGEMENT)
        # session.commit()
        session.flush()

    @staticmethod
    def _assign_permission_to_role(session, built_in_role: Role.BuiltInRole, *built_in_permissions):
        role = session.query(Role).filter(
            Role.name == built_in_role.value.name).first()  # type: Role
        for built_in_permission in built_in_permissions:  # type: Permission.BuiltInPermission
            permission = session.query(Permission).filter(
                Permission.label == built_in_permission.value.label).first()  # type: Permission
            role_permission = RolePermission(
                role_uuid=role.uuid,
                permission_uuid=permission.uuid,
            )
            session.add(role_permission)

    @staticmethod
    def _create_built_in_user(session):
        user = User(
            username='admin',
            email='admin@scholar.tool',
            password=authorization.toolkit.hash_plaintext('12345679'),
        )
        user.status = 1
        session.add(user)
        # session.commit()
        session.flush()

    @staticmethod
    def _assign_role_for_built_in_user(session):
        user = session.query(User).filter(User.username == 'admin').first()  # type: User
        role = session.query(Role).filter(Role.name == Role.BuiltInRole.ADMINISTRATOR.value.name).first()  # type: Role
        user_role = UserRole(
            user_uuid=user.uuid,
            role_uuid=role.uuid,
        )
        session.add(user_role)
        # session.commit()
        session.flush()

    @staticmethod
    def _create_scholar_account_for_built_in_user(session):
        user = session.query(User).filter(User.username == 'admin').first()  # type: User
        account = ScholarPaymentAccount(
            user_uuid=user.uuid,
            balance=0,
        )
        session.add(account)
        # session.commit()
        session.flush()

    @staticmethod
    def _create_default_event(session):
        user = session.query(User).filter(User.username == 'admin').first()  # type: User
        event = Event(
            author_uuid=user.uuid,
            title='欢迎使用 ScholarToolManager 项目',
            summary='这是一个默认公告',
            content="""
            祝好运
            """
        )
        session.add(event)
        # session.commit()
        session.flush()

    @staticmethod
    def _create_default_service_template(session):
        gb = 1024 * 1024 * 1024

        template0 = ServiceTemplate(
            service_type=ServiceTemplate.TYPE.DATA,
            title='2G流量套餐',
            subtitle='适合浏览网页，查找资料',
            description='2GB套餐流量#12个月有效期#基本技术支持',
            package=2 * gb,
            price=2 * 2 * 1024,
            initialization_fee=1024
        )
        session.add(template0)

        template1 = ServiceTemplate(
            service_type=ServiceTemplate.TYPE.DATA,
            title='3G流量套餐',
            subtitle='适合浏览网页，查找资料',
            description='3GB套餐流量#12个月有效期#基本技术支持',
            package=3 * gb,
            price=2 * 3 * 1024,
            initialization_fee=1024
        )
        session.add(template1)

        template2 = ServiceTemplate(
            service_type=ServiceTemplate.TYPE.DATA,
            title='4G流量套餐',
            subtitle='适合浏览网页，查找资料',
            description='4GB套餐流量#12个月有效期#基本技术支持',
            package=4 * gb,
            price=2 * 4 * 1024,
            initialization_fee=1024
        )
        session.add(template2)

        template3 = ServiceTemplate(
            service_type=ServiceTemplate.TYPE.DATA,
            title='5G流量套餐',
            subtitle='适合浏览网页，查找资料',
            description='5GB套餐流量#12个月有效期#基本技术支持',
            package=5 * gb,
            price=2 * 5 * 1024,
            initialization_fee=1024
        )
        session.add(template3)

        template4 = ServiceTemplate(
            service_type=ServiceTemplate.TYPE.MONTHLY,
            title='包月3G套餐',
            subtitle='适合浏览网页，查找资料',
            description='3GB套餐流量#1个月有效期#每月1号重置流量#基本技术支持',
            package=3 * gb,
            price=3 * 1024,
            initialization_fee=1024
        )
        session.add(template4)

        template5 = ServiceTemplate(
            service_type=ServiceTemplate.TYPE.MONTHLY,
            title='包月5G套餐',
            subtitle='适合浏览网页，查找资料',
            description='3GB套餐流量#1个月有效期#每月1号重置流量#基本技术支持',
            package=5 * gb,
            price=5 * 1024,
            initialization_fee=1024
        )
        session.add(template5)

        # session.commit()
        session.flush()

    @staticmethod
    def _create_built_in_payment_method(session):
        payment_method = PaymentMethod(
            name='学术积分账户余额'
        )
        session.add(payment_method)
        # session.commit()
        session.flush()


toolkit = ProjectInitializationToolkit()
