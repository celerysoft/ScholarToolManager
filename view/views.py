#!/usr/bin/python3
# -*-coding:utf-8 -*-

import markdown2
from flask import render_template, session, request, redirect, url_for, abort
from flask.views import View

import database

import exception
import model
import permission

app = None


def init_app(app_instance):
    global app
    app = app_instance


def derive_db_session(pagination=False):
    return database.derive_db_session(pagination)


__ITEM_PER_PAGE = None


def get_item_per_page():
    global __ITEM_PER_PAGE
    if __ITEM_PER_PAGE is None:
        __ITEM_PER_PAGE = app.config['ITEM_PER_PAGE']
    return __ITEM_PER_PAGE


__URL_OF_BLOG_IMAGE = None


def get_url_of_blog_image():
    global __URL_OF_BLOG_IMAGE
    if __URL_OF_BLOG_IMAGE is None:
        __URL_OF_BLOG_IMAGE = app.config['URL_OF_BLOG_IMAGE']
    return __URL_OF_BLOG_IMAGE


def derive_user_id_from_session():
    if 'user' in session.keys():
        return session['user']['id']
    else:
        return None


def login_required(f):
    def decorator(*args, **kwargs):
        permission.check_user_permission()
        return f(*args, **kwargs)

    return decorator


class RenderTemplateView(View):
    def __init__(self, template=None, title=None, **kwargs):
        self.template = template
        self.title = title
        self.kwargs = kwargs

    def dispatch_request(self):
        return render_template(self.template,
                               title=self.title,
                               **self.kwargs)


class BaseView(RenderTemplateView):
    pass


class UserView(RenderTemplateView):
    decorators = [login_required]


class PermissionRequiredView(UserView):
    def __init__(self, template=None, title=None, permission_func=None, **kwargs):
        super().__init__(template, title, **kwargs)
        self.permission_func = permission_func
        self._check_permission()

    def _check_permission(self):
        if self.permission_func is not None:
            if not self.permission_func(derive_db_session(), derive_user_id_from_session()):
                raise exception.http.Forbidden()


class LoginView(BaseView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template = 'login.html'
        self.title = '登录'

    def dispatch_request(self):
        debug = app.config['DEBUG']

        if session.get('user', None) is not None:
            return redirect(url_for('home_page'))

        return render_template(self.template,
                               title=self.title,
                               debug=debug,
                               **self.kwargs)


class RegisterView(BaseView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template = 'register.html'
        self.title = '注册'

    def dispatch_request(self):
        debug = app.config['DEBUG']

        if session.get('user', None) is not None:
            return redirect(url_for('home_page'))

        return render_template(self.template,
                               title=self.title,
                               debug=debug,
                               **self.kwargs)


class ManageInvitationView(PermissionRequiredView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template = 'manage_invitation.html'
        self.title = '邀请码管理'
        self.permission_func = permission.check_manage_invitation_code_permission

    def dispatch_request(self):
        db_session = derive_db_session(pagination=True)
        page = request.args.get('page')
        try:
            page = int(page) if page is not None else 1
        except ValueError:
            return redirect(url_for(request.endpoint))

        pagination = db_session.query(model.InvitationCode).order_by(model.InvitationCode.created_at.desc()).paginate(
            page, get_item_per_page(), False)
        if page > 1 and len(pagination.items) is 0:
            return redirect(url_for(request.endpoint))
        else:
            for invitation in pagination.items:
                inviter = db_session.query(model.User).filter_by(id=invitation.inviter_id).first()
                invitation.inviter_username = inviter.username
                if invitation.invitee_id is not None:
                    invitee = db_session.query(model.User).filter_by(id=invitation.invitee_id).first()
                    invitation.invitee_username = invitee.username

        return render_template(self.template,
                               title=self.title,
                               pagination=pagination,
                               pagination_url_for=request.endpoint,
                               **self.kwargs)


class ManageRoleView(PermissionRequiredView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template = 'manage_role.html'
        self.title = '角色管理'
        self.permission_func = permission.check_manage_role_permission

    def dispatch_request(self):
        db_session = derive_db_session(pagination=True)

        page = request.args.get('page')
        try:
            page = int(page) if page is not None else 1
        except ValueError:
            return redirect(url_for('manage_role'))

        pagination = db_session.query(model.Role).order_by(model.Role.id).paginate(
            page, get_item_per_page(), False)
        if page > 1 and len(pagination.items) is 0:
            return redirect(url_for('manage_role'))

        return render_template(self.template,
                               title=self.title,
                               pagination=pagination,
                               pagination_url_for=request.endpoint,
                               **self.kwargs)


class EditRoleView(PermissionRequiredView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template = 'manage_role_edit.html'
        self.title = '编辑角色'
        self.permission_func = permission.check_manage_role_permission

    def dispatch_request(self):
        id = request.args.get('id')
        return render_template(self.template,
                               title=self.title,
                               id=id,
                               action='PATCH',
                               **self.kwargs)


class ManageServiceTemplateView(PermissionRequiredView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template = 'manage_service_template.html'
        self.title = '套餐模版管理'
        self.permission_func = permission.check_manage_service_template_permission

    def dispatch_request(self):
        db_session = derive_db_session(pagination=True)

        page = request.args.get('page')
        try:
            page = int(page) if page is not None else 1
        except ValueError:
            return redirect(url_for(request.endpoint))

        pagination = db_session.query(model.ServiceTemplate).order_by(model.ServiceTemplate.id).paginate(
            page, get_item_per_page(), False)
        if page > 1 and len(pagination.items) is 0:
            return redirect(url_for(request.endpoint))

        return render_template(self.template,
                               title=self.title,
                               pagination=pagination,
                               pagination_url_for=request.endpoint,
                               **self.kwargs)


class CreateServiceTemplateView(PermissionRequiredView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template = 'manage_service_template_edit.html'
        self.title = '创建套餐'
        self.permission_func = permission.check_manage_service_template_permission

    def dispatch_request(self):
        service_type = request.args.get('type') if request.args.get('type') else 0

        return render_template(self.template,
                               title=self.title,
                               type=service_type,
                               action='POST',
                               **self.kwargs)


class EditServiceTemplateView(PermissionRequiredView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template = 'manage_service_template_edit.html'
        self.title = '编辑套餐'
        self.permission_func = permission.check_manage_service_template_permission

    def dispatch_request(self):
        service_template_id = request.args.get('id')

        return render_template(self.template,
                               title=self.title,
                               id=service_template_id,
                               action='PATCH',
                               **self.kwargs)


class ManageEventView(PermissionRequiredView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template = 'manage_event.html'
        self.title = '公告管理'
        self.permission_func = permission.check_manage_event_permission

    def dispatch_request(self):
        db_session = derive_db_session(pagination=True)

        page = request.args.get('page')
        try:
            page = int(page) if page is not None else 1
        except ValueError:
            return redirect(url_for('manage_event'))

        pagination = db_session.query(model.Event).order_by(model.Event.created_at.desc()).paginate(
            page, get_item_per_page(), False)
        if page > 1 and len(pagination.items) is 0:
            return redirect(url_for('manage_event'))
        else:
            for product in pagination.items:
                user = db_session.query(model.User).filter_by(id=product.user_id).first()
                product.user_name = user.name

        return render_template(self.template,
                               title=self.title,
                               pagination=pagination,
                               pagination_url_for=request.endpoint,
                               **self.kwargs)


class EditEventView(PermissionRequiredView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template = 'manage_event_edit.html'
        self.title = '编辑公告'
        self.permission_func = permission.check_manage_event_permission

    def dispatch_request(self):
        product_id = request.args.get('id')

        return render_template(self.template,
                               title=self.title,
                               id=product_id,
                               action='PATCH',
                               **self.kwargs)


class ManageUserView(PermissionRequiredView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template = 'manage_user.html'
        self.title = '用户管理'
        self.permission_func = permission.check_manage_user_permission

    def dispatch_request(self):
        db_session = derive_db_session(pagination=True)

        url = url_for('manage_user')
        page = request.args.get('page')
        try:
            page = int(page) if page is not None else 1
        except ValueError:
            return redirect(url)

        pagination = db_session.query(model.User).order_by(model.User.created_at).paginate(
            page, get_item_per_page(), False)
        if page > 1 and len(pagination.items) is 0:
            return redirect(url)

        return render_template(self.template,
                               title=self.title,
                               pagination=pagination,
                               pagination_url_for=request.endpoint,
                               action='PATCH',
                               **self.kwargs)


class EventView(UserView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template = 'event.html'
        self.title = '公告'

    def dispatch_request(self):
        page = request.args.get('page')
        try:
            page = int(page) if page is not None else 1
        except ValueError:
            return redirect(url_for(request.endpoint))

        db_session = derive_db_session(pagination=True)
        pagination = db_session.query(model.Event).order_by(model.Event.created_at.desc()).paginate(
            page, get_item_per_page(), False
        )
        if page > 1 and len(pagination.items) is 0:
            return redirect(url_for(request.endpoint))

        for evenet in pagination.items:
            user = db_session.query(model.User).filter_by(id=evenet.user_id).first()
            evenet.user_name = user.name
            evenet.user_image = user.image

        return render_template(self.template,
                               title=self.title,
                               pagination=pagination,
                               pagination_url_for=request.endpoint,
                               **self.kwargs)


class EventDetailView(UserView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template = 'event_view.html'
        self.title = '公告'

    def dispatch_request(self, event_id):
        db_session = derive_db_session()
        event = db_session.query(model.Event).filter_by(id=event_id).first()
        if event is None:
            return abort(404)

        user = db_session.query(model.User).filter_by(id=event.user_id).first()

        event.html_content = markdown2.markdown(event.content, extras=['fenced-code-blocks', 'tables', 'toc'])

        event.html_content = event.html_content.replace('{{ image }}', get_url_of_blog_image())

        event.tags = event.tag.split(' ')
        event.user_name = user.name
        event.user_image = user.image

        return render_template(self.template,
                               title=self.title,
                               event=event)


class UserProfileView(UserView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template = 'user.html'

    def dispatch_request(self, name):
        db_session = derive_db_session()
        user = db_session.query(model.User).filter_by(name=name).first()
        if user is None:
            return abort(404)

        return render_template(self.template,
                               title='用户' + name,
                               user=user)


class ProductDetailView(UserView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template = 'product_detail.html'
        self.title = '学术详情'

    def dispatch_request(self, service_id):
        user_id = derive_user_id_from_session()
        db_session = derive_db_session()

        user_service = db_session.query(model.UserService) \
            .filter(model.Service.id == service_id) \
            .filter(model.UserService.service_id == model.Service.id) \
            .filter(model.UserService.user_id == user_id).first()
        if user_service is None:
            return redirect(url_for('product'))

        return render_template(self.template,
                               title=self.title)


class CreateProductView(UserView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template = 'product_create.html'
        self.title = '获取新学术'

    def dispatch_request(self):
        permission.check_user_permission()

        db_session = derive_db_session()

        monthly_services = db_session.query(model.ServiceTemplate) \
            .filter(model.ServiceTemplate.type == model.ServiceTemplate.MONTHLY) \
            .filter(model.ServiceTemplate.available == True) \
            .all()
        for s in monthly_services:
            s.descriptions = s.description.split('#')

        data_services = db_session.query(model.ServiceTemplate) \
            .filter(model.ServiceTemplate.type == model.ServiceTemplate.DATA) \
            .filter(model.ServiceTemplate.available == True) \
            .all()
        for s in data_services:
            s.descriptions = s.description.split('#')

        return render_template(self.template,
                               title=self.title,
                               monthly_services=monthly_services,
                               data_services=data_services)


class PayProductView(UserView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template = 'product_pay.html'
        self.title = '支付'

    def dispatch_request(self, service_template_id):
        user_id = derive_user_id_from_session()

        db_session = derive_db_session()
        service_template = db_session.query(model.ServiceTemplate) \
            .filter(model.ServiceTemplate.id == service_template_id).first()
        if service_template is None:
            return abort(404)
        service_template.descriptions = service_template.description.split('#')
        service_template.total_price = service_template.price + service_template.initialization_fee

        user_scholar_balance = db_session.query(model.UserScholarBalance) \
            .filter(model.UserScholarBalance.user_id == user_id).first()
        balance = user_scholar_balance.balance

        return render_template(self.template,
                               title=self.title,
                               action='create',
                               service=service_template,
                               balance=balance)


class RenewProductView(UserView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template = 'product_pay.html'
        self.title = '续费'

    def dispatch_request(self, service_id):
        # 防止当前登录用户续费不属于自己的套餐
        user_id = derive_user_id_from_session()
        db_session = derive_db_session()

        user_service = db_session.query(model.UserService) \
            .filter(model.Service.id == service_id) \
            .filter(model.UserService.service_id == model.Service.id) \
            .filter(model.UserService.user_id == user_id).first()
        if user_service is None:
            return redirect(url_for('product'))

        service = db_session.query(model.Service).filter(model.Service.id == service_id).first()

        service_template = db_session.query(model.ServiceTemplate) \
            .filter(model.ServiceTemplate.id == service.template_id).first()
        if service_template is None:
            return abort(404)
        service_template.descriptions = service_template.description.split('#')
        service_template.total_price = service_template.price

        user_scholar_balance = db_session.query(model.UserScholarBalance) \
            .filter(model.UserScholarBalance.user_id == user_id).first()
        balance = user_scholar_balance.balance

        return render_template(self.template,
                               title=self.title,
                               action='renew',
                               service_id=service_id,
                               service=service_template,
                               auto_renew=service.auto_renew,
                               balance=balance)
