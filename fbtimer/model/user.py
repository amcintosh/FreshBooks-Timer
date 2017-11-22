import logging

from fbtimer.service.auth import authorize
from fbtimer.service.config import (
    read_user, write_token, write_business, MissingAuthError
)
from fbtimer.service.user import get_business


log = logging.getLogger(__name__)


class User:

    def __init__(self):
        try:
            self.token, business = read_user()
        except MissingAuthError:
            self.token = authorize()
            business = get_business(self.token)
            write_token(self.token)
            write_business(business[0], business[1], business[2])
        self.business_name, self.business_id, self.account_id = business

    def __str__(self):
        return 'User({}, {})'.format(self.business_name, self.business_id)
