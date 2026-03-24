import datetime

tz = TimeZone("Europe/Moscow")
def get_timezone_now():
    return datetime.datetime.now().astimezone(tz)
