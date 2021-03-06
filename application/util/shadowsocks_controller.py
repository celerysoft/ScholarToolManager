# -*-coding:utf-8 -*-
import socket

import os

import configs
from application.util import shadowsocks_config_manager

# address of the client
CLIENT_ADDRESS = configs.SS_CONTROLLER_UDS_CLIENT_ADDRESS


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
    client.settimeout(3)


connect()


# address of the server
SERVER_ADDRESS = configs.SS_SERVER_UDS_ADDRESS


# print('send "ping"')
# client.sendto(b'ping', SERVER_ADDRESS)
# print(client.recv(1506))  # You'll receive 'pong'
#
# print('send "add"')
# client.sendto(b'add: {"server_port":60000, "password":"7cd308cc059"}', SERVER_ADDRESS)
# print(client.recv(1506))  # You'll receive 'ok'
#
# print('send "remove"')
# client.sendto(b'remove: {"server_port":8001}', SERVER_ADDRESS)
# print(client.recv(1506))  # You'll receive 'ok'


def add_port(port, password):
    print('===========================')
    print('start adding port %s' % port)
    print('===========================')

    data = 'add: {"server_port": %s, "password":"%s"}' % (port, password)
    data = bytes(data, encoding='utf-8')

    transferring = True
    response = None
    global client
    while transferring:
        try:
            client.sendto(data, SERVER_ADDRESS)
            response = client.recv(1024)
            print(response)
            if response == b'ok':
                transferring = False
            else:
                continue
        except socket.timeout:
            connect()

    shadowsocks_config_manager.add_port(port, password)

    print('============================')
    print('finish adding port %s' % port)
    print('============================')


def remove_port(port):
    print('=============================')
    print('start removing port %s' % port)
    print('=============================')

    data = 'remove: {"server_port": %s}' % port
    data = bytes(data, encoding='utf-8')

    response = None
    transferring = True
    global client
    while transferring:
        try:
            client.sendto(data, SERVER_ADDRESS)
            response = client.recv(1024)
            print(response)
            if response == b'ok':
                transferring = False
            else:
                continue
        except socket.timeout:
            connect()

    shadowsocks_config_manager.remove_port(port)

    print('==============================')
    print('finish removing port %s' % port)
    print('==============================')


def recreate_shadowsocks_config_file(db_session, debug=False):
    """
    重新创建配置文件

    :param db_session:
    :param debug:
    :return:
    """
    shadowsocks_config_manager.recreate_shadowsocks_config_file(db_session, debug=debug)


def restart_service():
    pass
