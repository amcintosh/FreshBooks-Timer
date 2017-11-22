import logging

from fbtimer import FRESHBOOKS_BASE_URL
from fbtimer.model.timer import Timer
from fbtimer.service.auth import auth


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
