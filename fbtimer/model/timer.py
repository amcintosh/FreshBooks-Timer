import datetime
import logging

from dateutil import tz

from fbtimer.model import BaseModel
from fbtimer.util import parse_datetime_to_local, parse_datetime_to_utc


log = logging.getLogger(__name__)


class Timer(BaseModel):

    def __str__(self):
        if self.is_running:
            return 'Running: {}, started at {}'.format(
                datetime.timedelta(seconds=self.duration),
                self.start_time.strftime('%-I:%M %p')
            )
        return 'Paused: {}, started at {}'.format(
            datetime.timedelta(seconds=self.duration),
            self.start_time.strftime('%-I:%M %p')
        )

    @property
    def duration(self):
        duration = 0
        for time_entry in self.raw_data.get('time_entries'):
            if time_entry.get('duration'):
                duration = duration + time_entry.get('duration')
            else:
                duration = duration + (
                    datetime.datetime.utcnow().replace(tzinfo=tz.tzutc(), microsecond=0) -
                    parse_datetime_to_utc(time_entry['started_at'])
                ).total_seconds()
        return duration

    @property
    def active_time_entry(self):
        for time_entry in self.raw_data.get('time_entries'):
            if not time_entry.get('duration'):
                return time_entry

    @property
    def start_time(self):
        return parse_datetime_to_local(
            self.raw_data.get('time_entries')[0]['started_at']
        )

    @property
    def is_running(self):
        return self.raw_data.get('is_running', False)

    @property
    def client_id(self):
        return self.active_time_entry.get('client_id')

    @property
    def project_id(self):
        return self.active_time_entry.get('project_id')

    @property
    def has_client(self):
        active_time_entry = self.active_time_entry
        return active_time_entry.get('client_id') or active_time_entry.get('internal')
