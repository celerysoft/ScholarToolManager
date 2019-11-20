# -*- coding: utf-8 -*-
import json

import requests
from flask import make_response

import configs
from application import exception
from application.views.base_api import BaseAPI, ApiResult


class ReCaptchaApi(BaseAPI):
    methods = ['POST']

    def post(self):
        api_url = 'https://www.recaptcha.net/recaptcha/api/siteverify'

        g_response = self.get_post_data('response', require=True, error_message='参数错误，人机身份验证失败')

        if configs.DEBUG:
            secret_key = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'
        else:
            secret_key = configs.RE_CAPTCHA_SECRET_KEY

        data = {
            'secret': secret_key,
            'response': g_response,
        }

        response = requests.post(api_url, data)
        if response.ok:
            response_data = json.loads(response.text)  # type:dict

            if 'success' in response_data.keys() and response_data['success']:
                result = ApiResult('人机身份验证成功', 200)
                return make_response(result.to_response())
            else:
                raise exception.api.InvalidRequest('你没有通过人机身份验证')
        else:
            raise exception.api.ServiceUnavailable('获取人机身份验证结果失败，请稍后再试')


view = ReCaptchaApi
