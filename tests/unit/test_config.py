import os
import unittest
from unittest.mock import patch

import click
from freezegun import freeze_time

from fbtimer.service.config import read_user


class ConfigTests(unittest.TestCase):

    def setUp(self):
        pass

    @freeze_time("2017-11-24 21:01:01")
    @patch.object(click, 'get_app_dir')
    def test_read_user(self, mock_dir):
        mock_dir.return_value = os.path.join('tests', 'fixtures')

        expected_token = {
            'token_type': 'Bearer',
            'access_token': 'some_token',
            'refresh_token': 'some_other_token',
            'expires_in': 239.0
        }
        expected_business = ('My Business', 123, 'abc')

        token, business = read_user()

        self.assertDictEqual(token, expected_token)
        self.assertEqual(business, expected_business)
