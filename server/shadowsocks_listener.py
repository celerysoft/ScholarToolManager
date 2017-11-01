import json
import socket
import os
import urllib.request

import configs

if __name__ == '__main__':
    print('__main__')

# address of the client
# TODO 写到配置文件
CLIENT_ADDRESS = configs.Config.SS_LISTENER_UDS_CLIEND_ADDRESS
try:
    os.unlink(CLIENT_ADDRESS)
except OSError:
    if os.path.exists(CLIENT_ADDRESS):
        raise RuntimeError('wtf')

cli = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
cli.bind(CLIENT_ADDRESS)

# TODO 写到配置文件
SERVER_ADDRESS = configs.Config.SS_SERVER_UDS_ADDRESS

print('send "ping"')
cli.sendto(b'ping', SERVER_ADDRESS)
print(cli.recv(1506))  # You'll receive 'pong'

# print('send "add"')
# cli.sendto(b'add: {"server_port":60000, "password":"7cd308cc059"}', SERVER_ADDRESS)
# print(cli.recv(1506))  # You'll receive 'ok'
#
# print('send "remove"')
# cli.sendto(b'remove: {"server_port":8001}', SERVER_ADDRESS)
# print(cli.recv(1506))  # You'll receive 'ok'


while True:
    # when data is transferred on Shadowsocks, you'll receive stat info every 10 seconds
    msg = cli.recv(1506)
    print(msg)

    api_url = configs.Config.MAIN_SERVER_ADDRESS + '/api/usage'

    data = json.dumps(msg.decode('utf-8')).encode('utf-8')
    request = urllib.request.Request(api_url, data=msg, headers={'Content-type': 'application/json'})
    response = urllib.request.urlopen(request).read()
