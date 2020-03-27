# -*-coding:utf-8 -*-
"""
执行B系列定时任务
"""
from application.schedule.b001_cancel_overdue_order import CancelOverdueOrderScript

if __name__ == '__main__':
    script = CancelOverdueOrderScript()
    script.execute()
