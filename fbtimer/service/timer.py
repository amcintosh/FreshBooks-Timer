import json
import logging

from fbtimer import FRESHBOOKS_BASE_URL
from fbtimer.model.timer import Timer
from fbtimer.service.auth import auth
from fbtimer.util import parse_datetime_to_utc, utcnow_aware


log = logging.getLogger(__name__)


def get_timer(user):
    res = auth(user.token).get(
        '{}timetracking/business/{}/timers'.format(FRESHBOOKS_BASE_URL, user.business_id)
    ).json()

    if len(res.get('timers')) == 0:
        return None
    log.debug(res)
    return Timer(res.get('timers')[0])


def delete_timer(user, timer):
    res = auth(user.token).delete(
        '{}timetracking/business/{}/timers/{}'.format(
            FRESHBOOKS_BASE_URL, user.business_id, timer.id)
    )
    res.raise_for_status()


def log_timer(user, timer):
    for entry in timer.raw_data.get('time_entries'):
        del entry['active']
        del entry['identity_id']
        del entry['created_at']

    timer.raw_data.get('time_entries')[-1].update(
        duration=(
            utcnow_aware() - parse_datetime_to_utc(
                timer.raw_data.get('time_entries')[-1].get('started_at'))
        ).total_seconds(),
        timer={"id": timer.id}
    )

    res = auth(user.token).put(
        '{}timetracking/business/{}/timers/{}'.format(
            FRESHBOOKS_BASE_URL, user.business_id, timer.id),
        data=json.dumps({'timer': {'time_entries': timer.raw_data.get('time_entries')}})
    )
    log.debug(res.text)
    res.raise_for_status()
