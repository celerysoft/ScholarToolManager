import json
import socket
import os
import subprocess
import urllib.request, urllib.parse

if __name__ == '__main__':
    print('__main__')

# address of the client
CLIENT_ADDRESS = '/Users/admin/Developer/shadowsocks-controller-client.sock'
try:
    os.unlink(CLIENT_ADDRESS)
except OSError:
    if os.path.exists(CLIENT_ADDRESS):
        raise RuntimeError('wtf')

cli = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
cli.bind(CLIENT_ADDRESS)

SERVER_ADDRESS = '/Users/admin/Developer/shadowsocks-manager.sock'


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


def add_port(port, password):
    data = 'add: {"server_port":%s, "password":"%s"}' % (port, password)
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

    api_url = 'http://127.0.0.1:50001/api/ss'
    data = {
        'message': response.decode('utf-8'),
        'port': port,
        'password': '******'
    }
    data = json.dumps(data).encode('utf-8')
    request = urllib.request.Request(api_url, data=data, headers={'Content-type': 'application/json'})
    response = urllib.request.urlopen(request).read()
    print(response.decode('utf-8'))


def remove_port(port):
    data = 'remove: {"server_port":%s}' % port
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

    api_url = 'http://127.0.0.1:50001/api/ss'
    data = {
        'message': response.decode('utf-8'),
        'port': port,
        'password': '******'
    }
    data = json.dumps(data).encode('utf-8')
    request = urllib.request.Request(api_url, data=data, headers={'Content-type': 'application/json'})
    response = urllib.request.urlopen(request).read()
    print(response.decode('utf-8'))
