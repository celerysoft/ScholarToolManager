# -*-coding:utf-8 -*-
"""
将到期的学术服务标记为欠费
执行频率：每天执行
执行优先级：C-1
"""
from datetime import date

from application.model.service import Service
from application.util.database import session_scope


class MarkOverdueServiceAsOutOfCreditScript:
    def execute(self):
        today = date.today()
        with session_scope() as session:
            while True:
                services = session.query(Service) \
                    .filter(Service.status.in_([Service.STATUS.INITIALIZATION, Service.STATUS.ACTIVATED]),
                            Service.billing_date <= today) \
                    .limit(500).all()

                if services is None or len(services) == 0:
                    break

                for service in services:  # type: Service
                    service.status = Service.STATUS.OUT_OF_CREDIT

                session.commit()


script = MarkOverdueServiceAsOutOfCreditScript()


if __name__ == '__main__':
    # script = MarkOverdueServiceAsOutOfCreditScript()
    # script.execute()
    raise RuntimeError('Do not execute this script directory, execute c000_execute_c_series_schedules.py instead')
