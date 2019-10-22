import socket

import os

import configs
from util import shadowsocks_config_manager

# address of the client
CLIENT_ADDRESS = configs.Config.SS_CONTROLLER_UDS_CLIEND_ADDRESS


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


# address of the server
SERVER_ADDRESS = configs.Config.SS_SERVER_UDS_ADDRESS


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


def add_port(port, password, auto_restart_listener=True):
    print('===========================')
    print('start adding port %s' % port)
    print('===========================')

    data = 'add: {"server_port": %s, "password":"%s"}' % (port, password)
    data = bytes(data, encoding='utf-8')

    transferring = True
    response = None
    while transferring:
        try:
            client.sendto(data, SERVER_ADDRESS)
            response = client.recv(1024)
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

    if auto_restart_listener:
        restart_shadowsocks_listener()


def remove_port(port, auto_restart_listener=True):
    print('=============================')
    print('start removing port %s' % port)
    print('=============================')

    data = 'remove: {"server_port": %s}' % port
    data = bytes(data, encoding='utf-8')

    response = None
    transferring = True
    while transferring:
        try:
            client.sendto(data, SERVER_ADDRESS)
            response = client.recv(1024)
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

    if auto_restart_listener:
        restart_shadowsocks_listener()


def recreate_shadowsocks_config_file(db_session, debug=False):
    """
    重新创建配置文件

    :param db_session:
    :param debug:
    :return:
    """
    shadowsocks_config_manager.recreate_shadowsocks_config_file(db_session, debug=debug)


def restart_service(db_session):
    pass


def restart_shadowsocks_listener():
    pass
    # print('==============================')
    # print('restart shadowsocks listener')
    # print('==============================')
    # restart_shell_file = configs.Config.SS_LISTENER_RESTART_SHELL_FILE_PATH
    # status = os.system('. %s' % restart_shell_file)
