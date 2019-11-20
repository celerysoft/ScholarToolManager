# -*- coding: utf-8 -*-
import json

import requests
from flask import make_response, jsonify

from application import exception
from application.views.base_api import BaseAPI


class TodayInHistoryAPI(BaseAPI):
    methods = ['GET']

    def get(self):
        api_url = 'http://www.ipip5.com/today/api.php'
        params = {
            'type': 'json'
        }
        response = requests.get(api_url, params=params, verify=True)
        if response.ok:
            return make_response(jsonify(json.loads(response.text)), 200)
        else:
            raise exception.api.ServiceUnavailable('获取数据失败')


view = TodayInHistoryAPI
