import os
import configs
import model

# /config/multiple_users_config.json
__SHADOWSOCKS_CONFIG_FILE_PATH = configs.Config.SHADOWSOCKS_CONFIG_FILE_PATH
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

    for line in lines:
        if line.find('"%s": ' % port) > 0:
            lines.remove(line)

    with open(__SHADOWSOCKS_CONFIG_FILE_PATH, 'w') as f:
        f.writelines(lines)


def recreate_shadowsocks_config_file(db_session, method='aes-256-cfb', timeout=300):
    """

    :param db_session: SQLAlchemy
    :param method: Encryption method
    :param timeout: in seconds
    :return:
    """

    service_passwords = db_session.query(model.ServicePassword) \
        .filter(model.Service.alive.is_(True)) \
        .filter(model.Service.available.is_(True)) \
        .filter(model.ServicePassword.service_id == model.Service.id) \
        .order_by(model.ServicePassword.port).all()

    port1, password1 = 20000, 123321
    port2, password2 = 20001, 12345678
    lines = []
    lines.append('{%s' % os.linesep)
    lines.append('%s"server": "0.0.0.0",%s' % (__CONFIG_FILE_INDENT, os.linesep))
    lines.append('%s"port_password": {%s' % (__CONFIG_FILE_INDENT, os.linesep))

    service_password_count = len(service_passwords)
    for x in range(service_password_count):
        service_password = service_passwords[x]
        if x == service_password_count - 1:
            lines.append('%s%s"%s": "%s"%s'
                         % (__CONFIG_FILE_INDENT,
                            __CONFIG_FILE_INDENT,
                            service_password.port,
                            service_password.password,
                            os.linesep))
        else:
            lines.append('%s%s"%s": "%s",%s'
                         % (__CONFIG_FILE_INDENT,
                            __CONFIG_FILE_INDENT,
                            service_password.port,
                            service_password.password,
                            os.linesep))

    lines.append('%s},%s' % (__CONFIG_FILE_INDENT, os.linesep))
    lines.append('%s"timeout": %s,%s' % (__CONFIG_FILE_INDENT, timeout, os.linesep))
    lines.append('%s"method": "%s",%s' % (__CONFIG_FILE_INDENT, method, os.linesep))
    lines.append('%s"fast_open": false,%s' % (__CONFIG_FILE_INDENT, os.linesep))
    lines.append('%s"workers": 1%s' % (__CONFIG_FILE_INDENT, os.linesep))
    lines.append('}')

    with open(__SHADOWSOCKS_CONFIG_FILE_PATH, 'w') as f:
        f.writelines(lines)


if __name__ == '__main__':
    # add_port(56000, 'ss')
    # remove_port(56000)

    with open(__SHADOWSOCKS_CONFIG_FILE_PATH, 'r') as f:
        lines = f.readlines()
        print(lines)
