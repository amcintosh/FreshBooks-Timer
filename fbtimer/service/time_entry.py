from fbtimer import FRESHBOOKS_BASE_URL
from fbtimer.service.auth import auth
from fbtimer.util import zulu_time
from datetime import datetime
import logging
import json

log = logging.getLogger(__name__)


def create_new_time_entry(user):
    time_entry = {
        "time_entry": {
            "is_logged": False,
            # "note": "Stuff",
            # 'client_id': '2149780',\
            # 'project_id': '153125'\
            "started_at": zulu_time(datetime.utcnow())
        }
    }
    res = auth(user.token).post(
        '{}timetracking/business/{}/time_entries'.format(
            FRESHBOOKS_BASE_URL, user.business_id),
        data=json.dumps(time_entry)
    )
    log.debug('here')
    log.debug(res.text)
    res.raise_for_status()
    return res.json()
