# -*-coding:utf-8 -*-
"""
执行C系列定时任务
执行频率：每天执行
"""
from application.schedule.c001_mark_overdue_service_as_out_of_credit import MarkOverdueServiceAsOutOfCreditScript
from application.schedule.c005_suspend_overdue_service import SuspendOverdueServiceScript
from application.schedule.c010_remove_suspended_service import RemoveSuspendedServiceScript

if __name__ == '__main__':
    script = MarkOverdueServiceAsOutOfCreditScript()
    script.execute()

    script = SuspendOverdueServiceScript()
    script.execute()

    script = RemoveSuspendedServiceScript()
    script.execute()
