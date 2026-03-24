import datetime

import pytz

tz = pytz.timezone("Europe/Moscow")


def get_timezone_now():
    return datetime.datetime.now().astimezone(tz)


