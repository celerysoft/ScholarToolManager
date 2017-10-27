import datetime


def derive_1st_of_next_month(dt):
    if dt.month == 12:
        first_day = datetime.datetime(dt.year + 1, 1, 1).timestamp()
    else:
        first_day = datetime.datetime(dt.year, dt.month + 1, 1).timestamp()
    return first_day
