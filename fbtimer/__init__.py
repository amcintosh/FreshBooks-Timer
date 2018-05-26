import os

__version__ = '0.1.1'
__date__ = '2017/20/10'
__updated__ = '2018/27/04'
__author__ = 'Andrew McIntosh'
__copyright__ = 'Copyright 2017, Andrew McIntosh'
__license__ = 'MIT'


FRESHBOOKS_BASE_URL = os.getenv('FBTIMER_API_URL', 'https://api.freshbooks.com/')
