#!/usr/bin/python3
# -*-coding:utf-8 -*-
import logging
import socket
import time

import os

import requests

import configs

LOG_FILE = configs.Config.SS_LISTENER_LOG_FILE
logging.basicConfig(filename=LOG_FILE,
                    level=logging.INFO,
                    format='%(asctime)s - %(message)s')

# address of the client
CLIENT_ADDRESS = configs.Config.SS_LISTENER_UDS_CLIEND_ADDRESS

# client instance
client = None


def connect():
    try:
        os.unlink(CLIENT_ADDRESS)
    except OSError:
        if os.path.exists(CLIENT_ADDRESS):
            raise RuntimeError('wtf')

    global client

    client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    client.bind(CLIENT_ADDRESS)
    client.settimeout(10)


connect()


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

if SS_CLIENT == 'shadowsocks':
    client.sendto(b'ping', SERVER_ADDRESS)
    print(client.recv(1024))  # You'll receive 'pong'

while True:
    msg = None
    try:
        if SS_CLIENT == 'shadowsocks':
            # when data is transferred on shadowsocks, you'll receive stat info every 10 seconds
            msg = client.recv(1024)
            # now = datetime.datetime.now()
            # print('TIME[%s] || MESSAGE[%s]' % (now, msg))
            logging.info(msg.decode())
        elif SS_CLIENT == 'shadowsocks-libev':
            time.sleep(10)
            client.sendto(b'ping', SERVER_ADDRESS)
            msg = client.recv(1024)
            logging.info(msg.decode())
        else:
            raise RuntimeError(
                '尚未为{}进行流量监听的适配'.format(configs.Config.SS_CLIENT)
            )
    except socket.timeout:
        connect()

    if msg is None:
        continue

    api_url = configs.Config.MAIN_SERVER_ADDRESS + '/api/usage'

    data = msg.decode('utf-8')
    data = data[6:]

    response = requests.post(api_url, data=data)
    if not response.ok:
        print(response.text)
        logging.error(response.text)
