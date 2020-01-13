# -*- coding: utf-8 -*-
import json
from datetime import datetime

from flask import make_response, request

import configs
from application import exception

from application.model.legacy import model
from application.util import permission, background_task
from application.util.database import session_scope
from application.views.base_api import PermissionRequiredAPI, ApiResult


# TODO 移至后台管理接口
class UsageAPI(PermissionRequiredAPI):
    methods = ['GET', 'POST']
    permission_required_for_get = []
    permission_required_for_post = []

    def get(self):
        log_file = configs.SS_LISTENER_LOG_FILE

        with open(log_file, 'r') as f:
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

    def post(self):
        raise exception.api.ServiceUnavailable('多节点功能正正在建设中')


view = UsageAPI
