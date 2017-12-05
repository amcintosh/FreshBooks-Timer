from datetime import datetime
from dateutil import tz
import dateutil.parser


def get_local_tz():  # pragma: nocover
    '''For patching purposes'''
    return tz.tzlocal()


def parse_datetime_to_local(value):
    utc_zone = tz.tzutc()
    local_zone = get_local_tz()
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


def utcnow_aware():
    return datetime.utcnow().replace(tzinfo=tz.tzutc())
