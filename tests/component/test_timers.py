import json
import time
import unittest
from unittest.mock import MagicMock, Mock, patch

from click.testing import CliRunner
from freezegun import freeze_time
import httpretty
import requests

from fbtimer.cli import cli
from tests import get_fixture


class TimerTests(unittest.TestCase):

    def setUp(self):
        patcher = patch('fbtimer.model.user.read_user')
        self.addCleanup(patcher.stop)
        self.mock_user = patcher.start()
        self.mock_user.return_value = (
            {
                'token_type': 'Bearer',
                'access_token': 'some_token',
                'refresh_token': 'some_other_token',
                'expires_in': 1000
            },
            ('My Business', 123, 'abc')
        )

    @freeze_time("2017-11-24 21:01:01")
    @httpretty.activate
    @patch('fbtimer.service.timer.auth')
    def test_get_timer(self, mock_auth):
        mock_auth.return_value = requests
        httpretty.register_uri(
            httpretty.GET, 'https://api.freshbooks.com/timetracking/business/123/timers',
            body=json.dumps(get_fixture('timer')),
            status=200,
            content_type="application/json"
        )

        runner = CliRunner()
        result = runner.invoke(cli, ['show'])
        self.assertTrue(self.mock_user.called)
        self.assertEqual(httpretty.last_request().method, "GET")
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Running: 0:03:55, started at 3:57 PM\n')
