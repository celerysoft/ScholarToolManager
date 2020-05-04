# -*-coding:utf-8 -*-
"""
After upgrade v1.0  to v2.0,
the password hash has changed, u must explain to the old users
"""
from datetime import datetime, timedelta

import configs
from application.model.legacy.model import User as LegacyUser
from application.model.user import User
from application.model.user_login_log import UserLoginLog
from application.util import email_util
from application.util.database import session_scope, legacy_session_scope


class RequestOldUserReturnToolkit(object):
    def execute(self) -> bool:
        with legacy_session_scope() as legacy_session, session_scope() as session:
            try:
                self._send_email_to_old_user(legacy_session, session)
            except BaseException as e:
                if configs.DEBUG:
                    raise RuntimeError(e)
                return False
            return True

    def _send_email_to_old_user(self, legacy_session, session):
        with open('../../templates/request_old_user_return_email.html', 'r') as f:
            email_template = f.read()
        # print(email_template)

        now = datetime.now()
        users = session.query(User).filter(User.status == User.STATUS.ACTIVATED).all()
        for user in users:  # type: User
            login_log = session.query(UserLoginLog).filter(
                UserLoginLog.user_uuid == user.uuid).order_by(
                UserLoginLog.created_at.desc()).first()  # type: UserLoginLog
            if login_log is None:
                legacy_user = legacy_session.query(LegacyUser).filter(
                    LegacyUser.username == user.username,
                    LegacyUser.available.is_(True)).first()  # type: LegacyUser
                login_datetime = datetime.fromtimestamp(legacy_user.last_login_at)
            else:
                login_datetime = login_log.created_at
            diff_day = now - login_datetime
            diff_day = diff_day.days
            print('用户名：', user.username)
            print('上次登录：', diff_day, '天前')
            email_text = email_template.format(user.username, diff_day)
            email_util.toolkit.send_email(user.email, '『Celery Soft 学术』全新升级', email_text)


toolkit = RequestOldUserReturnToolkit()


if __name__ == '__main__':
    toolkit.execute()
