import logging

from fbtimer import FRESHBOOKS_BASE_URL
from fbtimer.model.client import Client
from fbtimer.service.auth import auth


log = logging.getLogger(__name__)


def get_recent_clients(user):
    res = auth(user.token).get(
        '{}accounting/account/{}/users/clients?page=1&per_page=5'
        '&search[vis_state]=0&sort=updated_desc'.format(FRESHBOOKS_BASE_URL, user.account_id)
    ).json()
    log.debug(res)

    clients = res['response']['result'].get('clients')
    if len(clients) == 0:
        return None
    return [Client(a) for a in clients]
