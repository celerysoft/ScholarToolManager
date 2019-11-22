# -*-coding:utf-8 -*-
import datetime


def derive_1st_of_next_month(dt: datetime.datetime = None) -> float:
    """
    derive 1st day's timestamp of next month.

    :param dt:
    :type dt: datetime.datetime
    :return: 1st day's timestamp of next month
    :rtype: float
    """
    if dt is None:
        dt = datetime.datetime.now()
    if dt.month == 12:
        first_day = datetime.datetime(dt.year + 1, 1, 1).timestamp()
    else:
        first_day = datetime.datetime(dt.year, dt.month + 1, 1).timestamp()
    return first_day


def derive_1st_datetime_of_next_month(dt: datetime.datetime = None) -> datetime.datetime:
    """
    derive 1st day's datetime object of next month.

    :param dt:
    :type dt: datetime.datetime
    :return: 1st day's datetime object of next month
    :rtype: datetime.datetime
    """
    if dt is None:
        dt = datetime.datetime.now()
    if dt.month == 12:
        first_day = datetime.datetime(dt.year + 1, 1, 1)
    else:
        first_day = datetime.datetime(dt.year, dt.month + 1, 1)
    return first_day


class DateToolkit(object):
    @staticmethod
    def derive_1st_of_next_month(dt: datetime.datetime = None) -> float:
        """
        derive 1st day's timestamp of next month.

        :param dt:
        :type dt: datetime.datetime
        :return: 1st day's timestamp of next month
        :rtype: float
        """
        if dt is None:
            dt = datetime.datetime.now()
        if dt.month == 12:
            first_day = datetime.datetime(dt.year + 1, 1, 1).timestamp()
        else:
            first_day = datetime.datetime(dt.year, dt.month + 1, 1).timestamp()
        return first_day

    @staticmethod
    def derive_1st_datetime_of_next_month(dt: datetime.datetime = None) -> datetime.datetime:
        """
        derive 1st day's datetime object of next month.

        :param dt:
        :type dt: datetime.datetime
        :return: 1st day's datetime object of next month
        :rtype: datetime.datetime
        """
        if dt is None:
            dt = datetime.datetime.now()
        if dt.month == 12:
            first_day = datetime.datetime(dt.year + 1, 1, 1)
        else:
            first_day = datetime.datetime(dt.year, dt.month + 1, 1)
        return first_day

    @staticmethod
    def datetime_to_str(dt: datetime.datetime) -> str:
        dt = dt if dt is not None else datetime.datetime.now()
        # return dt.strftime('%Y-%m-%d %H:%M:%S')
        return dt.isoformat()


toolkit = DateToolkit()
