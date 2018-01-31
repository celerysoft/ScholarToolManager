import ssl
import urllib.request
import json


def add_port():
    api_url = 'http://127.0.0.1:20000/api/test'

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    data = {
        'port': '12345',
        'password': '123456'
    }

    # noinspection PyUnresolvedReferences
    http_request = urllib.request.Request(api_url, json.dumps(data).encode(), method='POST', headers={'Content-type': 'application/json'})
    # noinspection PyUnresolvedReferences
    response = urllib.request.urlopen(http_request, context=context).read()


def remove_port():
    api_url = 'http://127.0.0.1:20000/api/test'

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    data = {
        'port': '12345',
    }

    # noinspection PyUnresolvedReferences
    http_request = urllib.request.Request(api_url, json.dumps(data).encode(), method='DELETE', headers={'Content-type': 'application/json'})
    # noinspection PyUnresolvedReferences
    response = urllib.request.urlopen(http_request, context=context).read()


if __name__ == '__main__':
    add_port()
    # remove_port()
