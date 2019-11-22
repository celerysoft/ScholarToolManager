# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime

from flask import make_response, request

import configs
from application import exception

from application.model import model
from application.util import permission, background_task
from application.util.database import session_scope
from application.views.base_api import BaseNeedLoginAPI, ApiResult


class UsageAPI(BaseNeedLoginAPI):
    methods = ['GET', 'POST']
    need_login_methods = ['GET']

    def get(self):
        with session_scope() as session:
            if not permission.check_manage_permission(session, self.user_id):
                raise exception.api.Forbidden("无权限")

        shadowsocks_log_file = configs.SS_LISTENER_LOG_FILE

        with open(shadowsocks_log_file, 'r') as f:
            lines = f.readlines()

        lines = lines[-10:] if len(lines) >= 10 else lines

        warning_message = None
        last_record = lines[-1] if len(lines) > 0 else None
        if last_record is not None:
            datetime_str = last_record.split(' - ')[0]
            last_record_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S,%f')
            if datetime.now().timestamp() - last_record_datetime.timestamp() > 12 * 60 * 60:
                warning_message = '最后一条记录产生于12小时之前，请检查是否需要重启监听服务'
            elif datetime.now().timestamp() - last_record_datetime.timestamp() < 0:
                warning_message = '最后一条记录产生在未来，我的天！请检查是否需要重启监听服务'
            else:
                warning_message = '监听服务运行正常'

        response_data = {
                'usages': lines,
                'warning_message': warning_message,
            }

        result = ApiResult('获取学术统计信息成功', 200, response_data)
        return make_response(result.to_response())

    def put(self):
        # TODO deprecated
        user_id = self.user_id
        if not self.valid_data(user_id):
            raise exception.api.Unauthorized('请先登录')

        with session_scope() as session:
            if not permission.check_manage_permission(session, user_id):
                raise exception.api.Forbidden("无权限")

        restart_shell_file = configs.SS_LISTENER_RESTART_SHELL_FILE_PATH
        status = os.system('. {}'.format(restart_shell_file))

        result = ApiResult('执行重启任务成功，返回信息：{}'.format(status), 201)
        return make_response(result.to_response())

    def post(self):
        # TODO 加强安全性

        with session_scope() as session:

            data = request.data.decode('utf-8')
            data = json.loads(data)
            for port, usage in data.items():
                # print('port %s use data: %s' % (port, usage))
                service = session.query(model.Service).filter(model.ServicePassword.port == port).filter(
                    model.Service.id == model.ServicePassword.service_id).first()  # type:model.Service

                if service is None:
                    continue

                if service.available:
                    if configs.SS_CLIENT == 'shadowsocks':
                        service.usage += usage
                        service.total_usage += usage
                    elif configs.SS_CLIENT == 'shadowsocks-libev':
                        diff = usage - service.last_usage
                        service.last_usage = usage
                        # 每个端口的流量统计信息会在每次被重新添加时归零，所以要考虑归零时的状态
                        if diff == 0:
                            continue
                        elif diff > 0:
                            service.usage += diff
                            service.total_usage += diff
                        else:
                            service.usage += usage
                            service.total_usage += usage
                    else:
                        raise exception.api.InternalServerError(
                            '尚未为{}进行流量统计接口的适配'.format(configs.SS_CLIENT)
                        )

                    if service.usage > service.package:
                        service.available = False
                        background_task.remove_port.delay(port=port)
                    if service.type == model.Service.DATA:
                        if service.expired_at < datetime.now():
                            service.available = False

            result = ApiResult('学术统计信息接收成功', 201)
            return make_response(result.to_response())


view = UsageAPI
