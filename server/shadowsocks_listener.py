import json
import socket
import os
import urllib.request

if __name__ == '__main__':
    print('__main__')

# address of the client
CLIENT_ADDRESS = '/Users/admin/Developer/shadowsocks-listener-client.sock'
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


while True:
    msg = cli.recv(1506)
    print(type(msg))
    print(msg)  # when data is transferred on Shadowsocks, you'll receive stat info every 10 seconds

    api_url = 'http://127.0.0.1:50001/api/usage'

    data = json.dumps(msg.decode('utf-8')).encode('utf-8')
    request = urllib.request.Request(api_url, data=msg, headers={'Content-type': 'application/json'})
    response = urllib.request.urlopen(request).read()
    print(response.decode('utf-8'))
