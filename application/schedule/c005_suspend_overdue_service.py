# -*-coding:utf-8 -*-
"""
暂停已欠费的学术服务
执行频率：每天执行
执行优先级：C-5
"""
from datetime import date, timedelta

from application.model.service import Service
from application.util import background_task
from application.util.database import session_scope


class SuspendOverdueServiceScript:
    THRESHOLD = timedelta(days=3)

    def execute(self):
        today = date.today()
        deadline = today - self.THRESHOLD
        with session_scope() as session:
            while True:
                services = session.query(Service) \
                    .filter(Service.status == Service.STATUS.OUT_OF_CREDIT,
                            Service.billing_date <= deadline) \
                    .limit(500).all()

                if services is None or len(services) == 0:
                    break

                for service in services:  # type: Service
                    try:
                        service.status = Service.STATUS.SUSPENDED
                        background_task.remove_port.delay(service.port)
                        session.commit()
                    except:
                        continue


script = SuspendOverdueServiceScript()


if __name__ == '__main__':
    script = SuspendOverdueServiceScript()
    script.execute()
