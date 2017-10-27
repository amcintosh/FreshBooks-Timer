from fbtimer.service.auth import make_req


def get_timer(user):
    res = make_req(
        user.token,
        'timetracking/business/{}/timers'.format(user.business_id)
    ).json()
    return res
