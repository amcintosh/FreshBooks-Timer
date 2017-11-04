import datetime
from dateutil import tz
import logging
from fbtimer.util import parse_datetime_to_local, parse_datetime_to_utc


log = logging.getLogger(__name__)


class Timer:

    def __init__(self, raw_timer):
        self.raw_timer = raw_timer

    @property
    def duration(self):
        duration = 0
        for time_entry in self.raw_timer.get('time_entries'):
            if time_entry.get('duration'):
                duration = duration + time_entry.get('duration')
            else:
                duration = duration + (
                    datetime.datetime.utcnow().replace(tzinfo=tz.tzutc(), microsecond=0) -
                    parse_datetime_to_utc(time_entry['started_at'])
                ).total_seconds()
        return duration

    @property
    def start_time(self):
        return parse_datetime_to_local(
            self.raw_timer.get('time_entries')[0]['started_at']
        )

    @property
    def is_running(self):
        return self.raw_timer.get('is_running', False)
