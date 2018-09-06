import logging

from fbtimer import FRESHBOOKS_BASE_URL
from fbtimer.model.project import Service
from fbtimer.service.auth import auth


log = logging.getLogger(__name__)


def get_service(user, service_id):
    res = auth(user.token, include_content_type=False).get(
        '{}projects/business/{}/service/{}'
        .format(FRESHBOOKS_BASE_URL, user.business_id, service_id)
    ).json()
    log.debug('Service response: %s', res)

    if res.get('service'):
        return Service(res.get('service'))
    return None
