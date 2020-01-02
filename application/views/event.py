# -*- coding: utf-8 -*-
import markdown2
from flask import make_response

import configs
from application import exception
from application.model.event import Event
from application.util import permission
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


class EventAPI(BaseNeedLoginAPI):
    methods = ['GET', 'POST', 'PATCH', 'DELETE']
    need_login_methods = ['GET', 'POST', 'PATCH', 'DELETE']

    def get(self):
        event_uuid = self.get_data('uuid')
        if self.valid_data(event_uuid):
            return self.get_event_detail(event_uuid)

        return self.get_events()

    def get_events(self):
        with session_scope() as session:
            query = self.derive_query_for_get_method(session, Event) \
                .filter(Event.status == Event.Status.VALID.value)
            page, page_size, offset, max_page = self.derive_page_parameter(query.count())

            events = query.offset(offset).limit(page_size).all()

            event_list = []
            for event in events:  # type:Event
                event_list.append(event.to_dict('content'))

            result = ApiResult('获取公告成功', payload={
                'events': event_list
            })
            return result.to_response()

    def get_event_detail(self, event_uuid):
        with session_scope() as session:
            event = session.query(Event).filter(Event.uuid == event_uuid).first()
            if event is None:
                raise exception.api.NotFound('公告不存在')

            data = event.to_dict()
            data['content'] = data['content'].replace('{{ image }}', configs.URL_OF_BLOG_IMAGE)

            html_version = self.get_data('html')
            if html_version:
                html_content = markdown2.markdown(event.content, extras=['fenced-code-blocks', 'tables', 'toc'])
                html_content = html_content.replace('{{ image }}', configs.URL_OF_BLOG_IMAGE)
                data['html'] = html_content

            result = ApiResult('获取公告成功', payload={
                'event': data
            })
            return result.to_response()

    # def post(self):
    #     name = self.get_post_data('name', require=True, error_message='公告标题不能为空')
    #     tag = self.get_post_data('tag')
    #     summary = self.get_post_data('summary', require=True, error_message='公告描述不能为空')
    #     content = self.get_post_data('content', require=True, error_message='公告内容不能为空')
    #
    #     with session_scope() as session:
    #         if not permission.toolkit.check_manage_event_permission(session, self.user_id):
    #             raise exception.api.Forbidden('用户无权创建公告')
    #
    #         event = Event(user_id=self.user_id, name=name.strip(), tag=tag, summary=summary.strip(),
    #                       content=content.strip())
    #
    #         session.add(event)
    #
    #         result = ApiResult('发布公告成功', 201)
    #         return make_response(result.to_response())

    # def patch(self):
    #     event_id = self.get_post_data('id', require=True, error_message='公告编号不能为空')
    #
    #     with session_scope() as session:
    #         if not permission.toolkit.check_manage_event_permission(session, self.user_id):
    #             raise exception.api.Forbidden('用户无权编辑公告')
    #
    #         event = session.query(Event).filter(Event.id == event_id).first()
    #         if event is None:
    #             raise exception.api.NotFound('需要编辑的公告不存在')
    #
    #         self.patch_model(Event, event)
    #
    #         result = ApiResult('编辑公告成功', 201)
    #         return make_response(result.to_response())

    # def delete(self):
    #     event_id = self.get_data('id')
    #     if not self.valid_data(event_id):
    #         event_id = self.get_post_data('id', require=True, error_message='所需删除的公告id不能为空')
    #
    #     with session_scope() as session:
    #         if not permission.toolkit.check_manage_event_permission(session, self.user_id):
    #             raise exception.api.Forbidden('当前用户无权删除公告')
    #
    #         event = session.query(Event) \
    #             .filter(Event.id == event_id, Event.available.is_(True)).first()  # type:Event
    #         if event is None:
    #             raise exception.api.NotFound('需要删除的公告不存在')
    #
    #         event.available = False
    #         # session.delete(event)
    #
    #         result = ApiResult('删除公告成功')
    #         return make_response(result.to_response())


view = EventAPI
