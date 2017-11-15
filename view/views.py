#!/usr/bin/python3
# -*-coding:utf-8 -*-
from flask import render_template
from flask.views import View
import permission


def login_required(f):
    def decorator(*args, **kwargs):
        permission.check_user_permission()
        return f(*args, **kwargs)

    return decorator


class RenderTemplateView(View):
    def __init__(self, template, title, **kwargs):
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
