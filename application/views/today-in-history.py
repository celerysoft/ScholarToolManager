# -*- coding: utf-8 -*-
import json
from datetime import datetime

import requests

from application import exception
from application.util.cache import cache
from application.util.dict import dict_toolkit
from application.views.base_api import BaseAPI, ApiResult


class TodayInHistoryAPI(BaseAPI):
    methods = ['GET']

    def get(self):
        cache_key = 'api-today-in-history-{}'.format(datetime.now().strftime('%Y-%m-%d'))
        today_in_history_json_str = cache.get(cache_key)
        if not self.valid_data(today_in_history_json_str):
            api_url = 'http://www.ipip5.com/today/api.php'
            params = {
                'type': 'json'
            }
            response = requests.get(api_url, params=params, verify=False)
            if response.ok:
                today_in_history_json_str = response.text
                cache.set(cache_key, today_in_history_json_str)
            else:
                raise exception.api.ServiceUnavailable('获取历史上的今天数据失败')

        try:
            payload = json.loads(today_in_history_json_str)
        except:
            cache.delete(cache_key)
            raise exception.api.ServiceUnavailable('获取历史上的今天数据失败，数据源返回的数据异常，请稍后再试')

        result = ApiResult('获取历史上的今天数据成功', payload=payload)
        return result.to_response()


view = TodayInHistoryAPI
