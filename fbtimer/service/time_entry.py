from datetime import datetime
import json
import logging

from fbtimer import FRESHBOOKS_BASE_URL
from fbtimer.service.auth import auth
from fbtimer.util import zulu_time, parse_datetime_to_utc, utcnow_aware

log = logging.getLogger(__name__)


def create_new_time_entry(user, timer=None):
    time_entry = {
        'time_entry': {
            'is_logged': False,
            # 'note': 'Stuff',
            # 'client_id': '2149780',\
            # 'project_id': '153125'\
            'started_at': zulu_time(datetime.utcnow())
        }
    }
    if timer:
        time_entry['time_entry'].update(
            timer={'id': timer.id}
        )

    res = auth(user.token).post(
        '{}timetracking/business/{}/time_entries'.format(
            FRESHBOOKS_BASE_URL, user.business_id),
        data=json.dumps(time_entry)
    )
    log.debug(res.text)
    res.raise_for_status()
    return res.json()


def pause_time_entry(user, timer):
    active_time_entry = timer.active_time_entry

    active_time_entry.update(
        is_logged=False,
        duration=(
            utcnow_aware() - parse_datetime_to_utc(active_time_entry.get('started_at'))
        ).total_seconds(),
        timer={'id': timer.id}
    )
    time_entry = {
        'time_entry': active_time_entry
    }

    res = auth(user.token).put(
        '{}timetracking/business/{}/time_entries/{}'.format(
            FRESHBOOKS_BASE_URL, user.business_id, active_time_entry.get('id')),
        data=json.dumps(time_entry)
    )
    log.debug(res.text)
    res.raise_for_status()
    return res.json()


def update_time_entry(user, timer, client_id=None, internal_client=False,
                      project_id=None, service_id=None, note=None):
    active_time_entry = timer.active_time_entry

    if client_id:
        active_time_entry['client_id'] = client_id
    elif internal_client:
        active_time_entry['client_id'] = None
        active_time_entry['internal'] = True
    if project_id:
        active_time_entry['project_id'] = project_id
    if service_id:
        active_time_entry['service_id'] = service_id
    if note:
        active_time_entry['note'] = note

    time_entry = {
        'time_entry': active_time_entry
    }

    res = auth(user.token).put(
        '{}timetracking/business/{}/time_entries/{}'.format(
            FRESHBOOKS_BASE_URL, user.business_id, active_time_entry.get('id')),
        data=json.dumps(time_entry)
    )
    log.debug(res.text)
    res.raise_for_status()
    return res.json()
