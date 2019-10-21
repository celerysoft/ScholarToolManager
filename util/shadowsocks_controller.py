import socket

import os

import configs
from util import shadowsocks_config_manager

if __name__ == '__main__':
    print('__main__')

# address of the client
CLIENT_ADDRESS = configs.Config.SS_CONTROLLER_UDS_CLIEND_ADDRESS
try:
    os.unlink(CLIENT_ADDRESS)
except OSError:
    if os.path.exists(CLIENT_ADDRESS):
        raise RuntimeError('wtf')

cli = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
cli.bind(CLIENT_ADDRESS)

# address of the server
SERVER_ADDRESS = configs.Config.SS_SERVER_UDS_ADDRESS


# print('send "ping"')
# cli.sendto(b'ping', SERVER_ADDRESS)
# print(cli.recv(1506))  # You'll receive 'pong'
#
# print('send "add"')
# cli.sendto(b'add: {"server_port":60000, "password":"7cd308cc059"}', SERVER_ADDRESS)
# print(cli.recv(1506))  # You'll receive 'ok'
#
# print('send "remove"')
# cli.sendto(b'remove: {"server_port":8001}', SERVER_ADDRESS)
# print(cli.recv(1506))  # You'll receive 'ok'


def add_port(port, password, auto_restart_listener=True):
    print('===========================')
    print('start adding port %s' % port)
    print('===========================')

    data = 'add: {"server_port": %s, "password":"%s"}' % (port, password)
    data = bytes(data, encoding='utf-8')

    transferring = True
    response = None
    while transferring:
        cli.sendto(data, SERVER_ADDRESS)
        response = cli.recv(1506)
        print(response)
        if response == b'ok':
            transferring = False
        else:
            continue

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
        cli.sendto(data, SERVER_ADDRESS)
        response = cli.recv(1506)
        if response == b'ok':
            transferring = False
        else:
            continue

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
    print('==============================')
    print('restart shadowsocks listener')
    print('==============================')
    restart_shell_file = configs.Config.SS_LISTENER_RESTART_SHELL_FILE_PATH
    status = os.system('. %s' % restart_shell_file)
