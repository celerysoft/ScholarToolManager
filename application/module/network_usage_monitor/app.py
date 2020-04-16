#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""
the doc for shadowsocks: https://github.com/shadowsocks/shadowsocks/wiki/Manage-Multiple-Users
the doc for shadowsocks-libev: https://github.com/shadowsocks/shadowsocks-libev/blob/master/doc/ss-manager.asciidoc
"""
import json
import logging
import socket
import time

import os

import configs
from application.model.service import Service
from application.util import background_task
from application.util.cache import cache
from application.util.database import session_scope

LOG_FILE = configs.SS_LISTENER_LOG_FILE
logging.basicConfig(filename=LOG_FILE,
                    level=logging.INFO,
                    format='%(asctime)s - %(message)s')


class NetworkUsageMonitor(object):
    # address of the client
    _CLIENT_ADDRESS = configs.SS_LISTENER_UDS_CLIENT_ADDRESS
    # address of the server
    _SERVER_ADDRESS = configs.SS_SERVER_UDS_ADDRESS
    # client name
    _SS_CLIENT = configs.SS_CLIENT

    _FREQUENCY = configs.SS_LISTENER_WORKING_FREQUENCY
    # client instance
    _client = None

    def _connect(self):
        try:
            os.unlink(self._CLIENT_ADDRESS)
        except OSError:
            if os.path.exists(self._CLIENT_ADDRESS):
                raise RuntimeError('wtf')

        self._client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self._client.bind(self._CLIENT_ADDRESS)
        self._client.settimeout(10)

    def _initialization_for_shadowsocks_libev(self):
        with session_scope() as session:
            services = session.query(Service).filter(
                Service.status.in_([Service.STATUS.ACTIVATED, Service.STATUS.OUT_OF_CREDIT])
            ).all()
            for service in services:  # type: Service
                cache_key = 'network-usage-monitor:port:{}'.format(service.port)
                cache.set(cache_key, service.usage)

    @staticmethod
    def _handle_port_usage(data: dict):
        with session_scope() as session:
            for port, usage in data.items():
                if usage <= 0:
                    continue

                service = session.query(Service).filter(
                    Service.port == port,
                    Service.status.in_([Service.STATUS.ACTIVATED, Service.STATUS.OUT_OF_CREDIT])
                ).first()  # type: Service

                if service is None:
                    background_task.remove_port.delay(port=port)

                service.usage += usage
                service.total_usage += usage

                if service.usage > service.package:
                    if service.status == Service.STATUS.ACTIVATED:
                        service.status = Service.STATUS.OUT_OF_CREDIT

                    if service.usage > int(service.package * 1.1):
                        service.status = Service.STATUS.SUSPENDED
                        background_task.remove_port.delay(port=port)

    def _handle_data_for_shadowsocks(self):
        # when data is transferred on shadowsocks, you'll receive stat info every 10 seconds
        # the stat format:
        # stat: {"8001":11370}
        # key is the port number, and value is the usage since last stat info received
        msg = self._client.recv(1024)  # type: bytes
        if msg is None or len(msg) == 0:
            return
        logging.info(msg.decode())

        # data = {"8001":11370}, convert stat to a json object
        try:
            data = json.loads(msg.decode('utf-8')[6:])
        except:
            return

        self._handle_port_usage(data)

    def _handle_data_for_shadowsocks_libev(self):
        time.sleep(self._FREQUENCY)
        # To receive the traffic statistics:
        # need to send a ping to server
        self._client.sendto(b'ping', self._SERVER_ADDRESS)
        # The format of the traffic statistics:
        # stat: {"8001":11370}
        msg = self._client.recv(1024)  # type: bytes
        if msg is None or len(msg) == 0:
            return
        logging.info(msg.decode())

        # data = {"8001":11370}, convert traffic statistics to a json object
        # key is the port number, and value is the total usage since the port is added
        # Note: There is no way to reset the traffic statistics, unless you remove the port and add it again
        try:
            data = json.loads(msg.decode('utf-8')[6:])  # type: dict
        except:
            return

        format_data = {}
        for port, usage in data.items():
            cache_key = 'network-usage-monitor:port:{}'.format(port)
            former_usage = cache.get(cache_key)
            cache.set(cache_key, usage)
            if former_usage is not None and len(former_usage) > 0:
                former_usage = int(former_usage)
                diff = usage - former_usage
                if diff >= 0:
                    format_data[port] = diff
                else:
                    format_data[port] = usage

        if len(format_data) > 0:
            self._handle_port_usage(format_data)

    def run(self):
        self._connect()

        if self._SS_CLIENT == 'shadowsocks':
            self._client.sendto(b'ping', self._SERVER_ADDRESS)
            print(self._client.recv(1024))  # You'll receive 'pong'
        elif self._SS_CLIENT == 'shadowsocks-libev':
            self._initialization_for_shadowsocks_libev()

        while True:
            try:
                if self._SS_CLIENT == 'shadowsocks':
                    self._handle_data_for_shadowsocks()
                elif self._SS_CLIENT == 'shadowsocks-libev':
                    self._handle_data_for_shadowsocks_libev()
                else:
                    raise RuntimeError(
                        '尚未为{}进行流量监听的适配'.format(configs.SS_CLIENT)
                    )
            except socket.timeout:
                self._connect()

    def run_test_for_shadowsocks_libev(self):
        self._initialization_for_shadowsocks_libev()

        while True:
            time.sleep(self._FREQUENCY)
            msg = self._generate_fake_data_for_shadowsocks_libev()
            logging.info(msg)
            print('\n')
            print('=' * 50)
            print('收到用量消息：\n{}'.format(msg))
            try:
                data = json.loads(msg[6:])  # type: dict
            except:
                return
            if len(data) == 0:
                exit(0)

            format_data = {}
            for port, usage in data.items():
                cache_key = 'network-usage-monitor:port:{}'.format(port)
                former_usage = cache.get(cache_key)
                cache.set(cache_key, usage)
                if former_usage is not None and len(former_usage) > 0:
                    former_usage = int(former_usage)
                    diff = usage - former_usage
                    if diff >= 0:
                        format_data[port] = diff
                    else:
                        format_data[port] = usage

            if len(format_data) > 0:
                self._handle_port_usage(format_data)
            print('消息处理完毕')
            print('=' * 50, '\n')

    def _generate_fake_data_for_shadowsocks_libev(self) -> str:
        # stat: {"8001":11370}
        from random import random
        from random import seed
        from datetime import datetime
        seed(int(datetime.now().timestamp()))
        data = {}
        with session_scope() as session:
            services = session.query(Service).filter(
                Service.status.in_([Service.STATUS.ACTIVATED, Service.STATUS.OUT_OF_CREDIT])
            ).all()
            for service in services:  # type: Service
                min_usage = 1024
                max_usage = 1024 * 1024
                random_number = random()
                usage = int(min_usage + (random_number * (max_usage - min_usage)))
                # print('usage: ', usage,
                #       '\t\tgross_usage: ', service.usage + usage,
                #       '\t\tpackage: {}'.format(service.package),
                #       '\t\tremaining_percentage: {}%'.format(
                #           round((1 - (service.usage + usage) / service.package) * 100, 2)))
                data[service.port] = usage + service.usage

        data_str = 'stat: {}'.format(json.dumps(data))
        return data_str


if __name__ == '__main__':
    monitor_service = NetworkUsageMonitor()
    monitor_service.run()
    # monitor_service.run_test_for_shadowsocks_libev()
