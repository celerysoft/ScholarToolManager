# -*- coding: utf-8 -*-
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import make_response

import configs
from application import exception
from application.views.base_api import BaseAPI, ApiResult


class ReCaptchaApi(BaseAPI):
    methods = ['POST']

    def post(self):
        api_url = 'https://www.recaptcha.net/recaptcha/api/siteverify'

        g_response = self.get_post_data('response')

        if configs.DEBUG:
            secret_key = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'
        else:
            secret_key = configs.RE_CAPTCHA_SECRET_KEY

        data = {
            'secret': secret_key,
            'response': g_response,
        }
        data = urlencode(data).encode()
        # noinspection PyUnresolvedReferences
        http_request = Request(api_url, method='POST', data=data)
        try:
            # noinspection PyUnresolvedReferences
            response = urlopen(http_request).read()
        except BaseException:
            raise exception.api.ServiceUnavailable('人机身份验证过程发生未知错误')

        response_dict = json.loads(response)
        if response_dict['success']:
            result = ApiResult('人机身份验证成功', 200)
        else:
            result = ApiResult('你没有通过人机身份验证', 400)

        return make_response(result.to_response())


view = ReCaptchaApi
