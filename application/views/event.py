# -*- coding: utf-8 -*-
import markdown2
from flask import make_response

import configs
from application import exception
from application.model.legacy.model import to_dict, Event
from application.util import permission
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


class EventAPI(BaseNeedLoginAPI):
    methods = ['GET', 'POST', 'PATCH', 'DELETE']
    need_login_methods = ['POST', 'PATCH', 'DELETE']

    def get(self):
        event_id = self.get_data('id')
        if self.valid_data(event_id):
            return self.get_event_detail(event_id)

        return self.get_events()

    def get_events(self):
        raise exception.api.InvalidRequest('')

    def get_event_detail(self, event_id):
        with session_scope() as db_session:
            event = db_session.query(Event).filter_by(id=event_id).first()
            if event is None:
                return self.api_document('id为%s的公告不存在' % event_id, 404)

            data = to_dict(event)

            html_version = self.get_data('html')
            if html_version:
                html_content = markdown2.markdown(event.content, extras=['fenced-code-blocks', 'tables', 'toc'])
                html_content = html_content.replace('{{ image }}', configs.URL_OF_BLOG_IMAGE)
                data['html'] = html_content

            result = ApiResult('获取公告成功', payload={
                'event': data
            })
            return make_response(result.to_response())

    def post(self):
        name = self.get_post_data('name', require=True, error_message='公告标题不能为空')
        tag = self.get_post_data('tag')
        summary = self.get_post_data('summary', require=True, error_message='公告描述不能为空')
        content = self.get_post_data('content', require=True, error_message='公告内容不能为空')

        with session_scope() as session:
            if not permission.toolkit.check_manage_event_permission(session, self.user_id):
                raise exception.api.Forbidden('用户无权创建公告')

            event = Event(user_id=self.user_id, name=name.strip(), tag=tag, summary=summary.strip(),
                          content=content.strip())

            session.add(event)

            result = ApiResult('发布公告成功', 201)
            return make_response(result.to_response())

    def patch(self):
        event_id = self.get_post_data('id', require=True, error_message='公告编号不能为空')

        with session_scope() as session:
            if not permission.toolkit.check_manage_event_permission(session, self.user_id):
                raise exception.api.Forbidden('用户无权编辑公告')

            event = session.query(Event).filter(Event.id == event_id).first()
            if event is None:
                raise exception.api.NotFound('需要编辑的公告不存在')

            self.patch_model(Event, event)

            result = ApiResult('编辑公告成功', 201)
            return make_response(result.to_response())

        # # TODO OAUTH
        # user_id = derive_user_id_from_session()
        # db_session = derive_db_session()
        # if user_id is None:
        #     return self.api_document('Need user_id')
        # if not permission.check_manage_event_permission(db_session, user_id):
        #     raise exception.api.Forbidden('ID为%s的用户无权编辑公告' % user_id)
        #
        # id = request.json['id']
        # name = request.json['name']
        # tag = request.json['tag']
        # summary = request.json['summary']
        # content = request.json['content']
        #
        # if not name or not name.strip():
        #     return self.api_document('公告名字不能为空', 400)
        # if not summary or not summary.strip():
        #     return self.api_document('公告描述不能为空', 400)
        # if not content or not content.strip():
        #     return self.api_document('公告内容不能为空', 400)
        #
        # db_session.query(model.Event).filter_by(id=id).update({
        #     'name': name,
        #     'tag': tag,
        #     'summary': summary,
        #     'content': content
        # })
        #
        # try:
        #     db_session.commit()
        # except BaseException as e:
        #     log_exception(e)
        #     return self.api_document('服务器内部错误，请刷新重试', 500)
        # except sqlalchemy.exc.DataError as e:
        #     db_session.rollback()
        #     return abort(make_response(str(e), 500))
        # finally:
        #     db_session.close()
        #
        # return make_response(
        #     jsonify({
        #         'message': '修改公告成功',
        #         'documentation_url': self._API_DOCUMENTATION_URL
        #     }), 201
        # )

    def delete(self):
        event_id = self.get_data('id')
        if not self.valid_data(event_id):
            event_id = self.get_post_data('id', require=True, error_message='所需删除的公告id不能为空')

        with session_scope() as session:
            if not permission.toolkit.check_manage_event_permission(session, self.user_id):
                raise exception.api.Forbidden('当前用户无权删除公告')

            event = session.query(Event) \
                .filter(Event.id == event_id, Event.available.is_(True)).first()  # type:Event
            if event is None:
                raise exception.api.NotFound('需要删除的公告不存在')

            event.available = False
            # session.delete(event)

            result = ApiResult('删除公告成功')
            return make_response(result.to_response())


view = EventAPI
