import logging
from fbtimer.service.auth import authorize
from fbtimer.service.user import read_token, write_token, MissingAuthError

log = logging.getLogger(__name__)


class User:

    def __init__(self):
        try:
            self.token = read_token()
        except MissingAuthError:
            self.token = authorize()
            write_token(self.token)
