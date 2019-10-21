#!/usr/bin/python3
# -*-coding:utf-8 -*-

import datetime
import json
import logging
import socket
import time

import os
import urllib.request

import configs

if __name__ == '__main__':
    print('__main__')

LOG_FILE = configs.Config.SS_LISTENER_LOG_FILE
logging.basicConfig(filename=LOG_FILE,
                    level=logging.DEBUG,
                    format='%(asctime)s - %(message)s')

# address of the client
CLIENT_ADDRESS = configs.Config.SS_LISTENER_UDS_CLIEND_ADDRESS
try:
    os.unlink(CLIENT_ADDRESS)
except OSError:
    if os.path.exists(CLIENT_ADDRESS):
        raise RuntimeError('wtf')

cli = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
cli.bind(CLIENT_ADDRESS)

SERVER_ADDRESS = configs.Config.SS_SERVER_UDS_ADDRESS

# print('send "ping"')
# cli.sendto(b'ping', SERVER_ADDRESS)
# print(cli.recv(1024))  # You'll receive 'pong' or transfer statistics

# print('send "add"')
# cli.sendto(b'add: {"server_port":60000, "password":"7cd308cc059"}', SERVER_ADDRESS)
# print(cli.recv(1024))  # You'll receive 'ok'
#
# print('send "remove"')
# cli.sendto(b'remove: {"server_port":8001}', SERVER_ADDRESS)
# print(cli.recv(1024))  # You'll receive 'ok'

SS_CLIENT = configs.Config.SS_CLIENT

while True:
    msg = None
    if SS_CLIENT == 'shadowsocks':
        # when data is transferred on Shadowsocks, you'll receive stat info every 10 seconds
        msg = cli.recv(1024)
        now = datetime.datetime.now()
        # print('TIME[%s] || MESSAGE[%s]' % (now, msg))
        logging.info(msg.decode())
    elif SS_CLIENT == 'shadowsocks-libev':
        time.sleep(10)
        cli.sendto(b'ping', SERVER_ADDRESS)
        msg = cli.recv(1024)
    else:
        raise RuntimeError(
            '尚未为{}进行流量监听的适配'.format(configs.Config.SS_CLIENT)
        )

    if msg is None:
        continue

    api_url = configs.Config.MAIN_SERVER_ADDRESS + '/api/usage'

    data = msg.decode('utf-8')
    data = data[6:].encode()
    # data = json.dumps(msg.decode('utf-8')).encode('utf-8')
    request = urllib.request.Request(api_url, data=msg, headers={'Content-type': 'application/json'})

    # noinspection PyBroadException
    try:
        response = urllib.request.urlopen(request).read()
    except BaseException as e:
        logging.error(msg.decode())
