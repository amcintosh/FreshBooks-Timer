import logging

from fbtimer.model import BaseModel

log = logging.getLogger(__name__)


class Client(BaseModel):

    def __str__(self):
        full_name = '{} {}'.format(self.raw_data.get('fname'), self.raw_data.get('lname'))

        if full_name == self.raw_data.get('organization'):
            return full_name

        return '{} ({})'.format(self.raw_data.get('organization'), full_name)
