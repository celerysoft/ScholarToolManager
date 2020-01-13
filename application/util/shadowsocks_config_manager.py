# -*-coding:utf-8 -*-
import os
import re

import configs

# /config/multiple_users_config.json
from application.model.service import Service

__SHADOWSOCKS_CONFIG_FILE_PATH = configs.SHADOWSOCKS_CONFIG_FILE_PATH
__CONFIG_FILE_INDENT = '  '


def add_port(port, password):
    """

    :param port:
    :param password:
    :return:
    """
    lines = []
    with open(__SHADOWSOCKS_CONFIG_FILE_PATH, 'r') as f:
        lines = f.readlines()
        line_count = len(lines)
        for x in range(line_count):
            if lines[x].find('port_password') > 0:
                lines.insert(x + 1, '%s%s"%s": "%s",%s'
                             % (__CONFIG_FILE_INDENT, __CONFIG_FILE_INDENT, port, password, os.linesep))
                break

    with open(__SHADOWSOCKS_CONFIG_FILE_PATH, 'w') as f:
        f.writelines(lines)


def remove_port(port):
    """

    :param port:
    :return:
    """
    lines = []
    with open(__SHADOWSOCKS_CONFIG_FILE_PATH, 'r') as f:
        lines = f.readlines()

    for index, line in enumerate(lines):
        m = re.match(r'^\s*"%s": ".*",.*$' % port, line)
        if m is not None:
            lines.remove(line)
        else:
            m = re.match(r'^\s*"%s": ".*".*$' % port, line)
            if m is not None:
                former_line = lines[index - 1]
                last_index = former_line.rindex(',')
                former_line = former_line[:last_index] + former_line[last_index + 1:]
                lines[index - 1] = former_line

                lines.remove(line)

    with open(__SHADOWSOCKS_CONFIG_FILE_PATH, 'w') as f:
        f.writelines(lines)


def recreate_shadowsocks_config_file(db_session, method='chacha20-ietf-poly1305', plugin='obfs-server',
                                     plugin_opts='obfs=tls', timeout=300, debug=False):
    """

    :param db_session: SQLAlchemy
    :param method: Encryption method
    :param plugin:
    :param plugin_opts:
    :param timeout: in seconds
    :param debug:
    :return:
    """
    services = db_session.query(Service) \
        .filter(Service.status.in_([Service.STATUS.ACTIVATED, Service.STATUS.OUT_OF_CREDIT])) \
        .all()

    lines = []
    lines.append('{%s' % os.linesep)
    if debug:
        lines.append('%s"server": "127.0.0.1",%s' % (__CONFIG_FILE_INDENT, os.linesep))
    else:
        lines.append('%s"server": "0.0.0.0",%s' % (__CONFIG_FILE_INDENT, os.linesep))
    lines.append('%s"port_password": {%s' % (__CONFIG_FILE_INDENT, os.linesep))

    service_password_count = len(services)
    if service_password_count == 0:
        lines.append('%s%s"%s": "%s"%s'
                     % (__CONFIG_FILE_INDENT,
                        __CONFIG_FILE_INDENT,
                        '59999',
                        'celerysoft.com',
                        os.linesep))
    else:
        for x in range(service_password_count):
            service = services[x]  # type: Service
            if x == service_password_count - 1:
                lines.append('%s%s"%s": "%s"%s'
                             % (__CONFIG_FILE_INDENT,
                                __CONFIG_FILE_INDENT,
                                service.port,
                                service.password,
                                os.linesep))
            else:
                lines.append('%s%s"%s": "%s",%s'
                             % (__CONFIG_FILE_INDENT,
                                __CONFIG_FILE_INDENT,
                                service.port,
                                service.password,
                                os.linesep))

    lines.append('%s},%s' % (__CONFIG_FILE_INDENT, os.linesep))
    lines.append('%s"timeout": %s,%s' % (__CONFIG_FILE_INDENT, timeout, os.linesep))
    lines.append('%s"method": "%s",%s' % (__CONFIG_FILE_INDENT, method, os.linesep))
    lines.append('%s"plugin": "%s",%s' % (__CONFIG_FILE_INDENT, plugin, os.linesep))
    lines.append('%s"plugin_opts": "%s",%s' % (__CONFIG_FILE_INDENT, plugin_opts, os.linesep))
    lines.append('%s"fast_open": false,%s' % (__CONFIG_FILE_INDENT, os.linesep))
    lines.append('%s"workers": 1%s' % (__CONFIG_FILE_INDENT, os.linesep))
    lines.append('}')

    with open(__SHADOWSOCKS_CONFIG_FILE_PATH, 'w') as f:
        f.writelines(lines)


if __name__ == '__main__':
    with open(__SHADOWSOCKS_CONFIG_FILE_PATH, 'r') as f:
        lines = f.readlines()
        print(lines)
