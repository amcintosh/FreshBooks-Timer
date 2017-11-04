from fbtimer import FRESHBOOKS_BASE_URL
from fbtimer.service.auth import auth
from fbtimer.model.timer import Timer


def get_timer(user):
    res = auth(user.token).get(
        '{}timetracking/business/{}/timers'.format(FRESHBOOKS_BASE_URL, user.business_id)
    ).json()

    if len(res.get('timers')) == 0:
        return None
    return Timer(res.get('timers')[0])
