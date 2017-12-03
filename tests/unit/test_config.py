from mock import patch
import os
import tempfile
import unittest

import click
from freezegun import freeze_time

from fbtimer.service.config import read_user, write_business, write_token


class ConfigTests(unittest.TestCase):

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

    @freeze_time("2017-11-24 21:01:01")
    @patch('fbtimer.service.config._get_config_path')
    def test_write(self, mock_conf):
        temp_file = tempfile.mkstemp()
        mock_conf.return_value = temp_file[1]

        write_token({
            'access_token': 'written_token',
            'refresh_token': 'another_written_token',
            'expires_at': 1511557600
        })
        write_business('My Written Business', 321, 'xyz')

        token, business = read_user()

        self.assertDictEqual(token, {
            'token_type': 'Bearer',
            'access_token': 'written_token',
            'refresh_token': 'another_written_token',
            'expires_in': 339.0
        })
        self.assertEqual(business, ('My Written Business', 321, 'xyz'))
