import dateutil.parser
from dateutil import tz


def parse_datetime_to_local(value):
    utc_zone = tz.tzutc()
    local_zone = tz.tzlocal()
    start_time = dateutil.parser.parse(value)
    start_time = start_time.replace(tzinfo=utc_zone)
    return start_time.astimezone(local_zone)


def parse_datetime_to_utc(value):
    utc_zone = tz.tzutc()
    start_time = dateutil.parser.parse(value)
    start_time = start_time.replace(tzinfo=utc_zone)
    return start_time


def zulu_time(value):
    return value.isoformat() + 'Z'
