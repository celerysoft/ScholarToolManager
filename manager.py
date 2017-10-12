import socket
import os

if __name__ == '__main__':
    print('__main__')
    pass

# address of the client
CLIENT_ADDRESS = '/Users/admin/Developer/shadowsocks-client.sock'
try:
    os.unlink(CLIENT_ADDRESS)
except OSError:
    if os.path.exists(CLIENT_ADDRESS):
        raise RuntimeError('wtf')

cli = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
cli.bind(CLIENT_ADDRESS)

SERVER_ADDRESS = '/Users/admin/Developer/shadowsocks-manager.sock'

print('send "ping"')
cli.sendto(b'ping', SERVER_ADDRESS)
print(cli.recv(1506))  # You'll receive 'pong'

# print('send "add"')
# cli.sendto(b'add: {"server_port":8001, "password":"7cd308cc059"}', SERVER_ADDRESS)
# print(cli.recv(1506))  # You'll receive 'ok'
#
# print('send "remove"')
# cli.sendto(b'remove: {"server_port":8001}', SERVER_ADDRESS)
# print(cli.recv(1506))  # You'll receive 'ok'

while True:
    print(cli.recv(1506))  # when data is transferred on Shadowsocks, you'll receive stat info every 10 seconds

