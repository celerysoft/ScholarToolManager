# -*- coding: utf-8 -*-
from application import exception
from application.model.event import Event
from application.model.service_template import ServiceTemplate
from application.model.user import User
from application.util.database import session_scope
from application.views.base_api import PermissionRequiredAPI, ApiResult


class ManagementEventAPI(PermissionRequiredAPI):
    methods = ['GET', 'POST', 'PUT', 'DELETE']
    permission_required_for_get = []
    permission_required_for_post = []
    permission_required_for_put = []
    permission_required_for_delete = []

    def get(self):
        with session_scope() as session:
            event_list = []
            query = self.derive_query_for_get_method(session, Event) \
                .filter(Event.status != Event.Status.DELETED.value)
            page, page_size, offset, max_page = self.derive_page_parameter(query.count())
            events = query.limit(page_size).offset(offset).all()
            for event in events:  # type: Event
                event_dict = event.to_dict('content')
                author_username = session.query(User.username) \
                    .filter(User.uuid == event.author_uuid,
                            User.status != User.STATUS.DELETED).first()
                author_username = author_username.username if author_username is not None else ''
                event_dict['author_username'] = author_username
                event_list.append(event_dict)

            result = ApiResult('获取公告成功', payload={
                'events': event_list,
                'page': page,
                'page_size': page_size,
                'max_page': max_page,
            })
            return result.to_response()

    def post(self):
        with session_scope() as session:
            event = self.create_model_from_http_post(Event)
            session.add(event)
            session.flush()

            result = ApiResult('发布公告成功', 201, payload={
                'event': event.to_dict(),
            })
            return result.to_response()

    def put(self):
        with session_scope() as session:
            event = self.update_model(session, Event)

            result = ApiResult('修改公告成功', 200, payload={
                'event': event.to_dict(),
            })
            return result.to_response()

    def delete(self):
        with session_scope() as session:
            self.delete_model(session, Event,
                              delete_status=Event.Status.DELETED.value,
                              not_found_error_message='需要删除的公告不存在')
            result = ApiResult('删除公告成功')
            return result.to_response()


view = ManagementEventAPI
