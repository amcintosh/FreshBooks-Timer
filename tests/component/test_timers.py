import json
from mock import patch
import unittest

from dateutil import tz
from click.testing import CliRunner
from freezegun import freeze_time
import httpretty
import requests

from fbtimer.cli import cli
from tests import get_fixture


class TimerTests(unittest.TestCase):

    def setUp(self):
        user_patcher = patch('fbtimer.model.user.read_user')
        self.mock_user = user_patcher.start()
        self.mock_user.return_value = (
            {
                'token_type': 'Bearer',
                'access_token': 'some_token',
                'refresh_token': 'some_other_token',
                'expires_in': 1000
            },
            ('My Business', 123, 'abc')
        )
        auth_patcher = patch('fbtimer.service.timer.auth')
        self.mock_auth = auth_patcher.start()
        self.mock_auth.return_value = requests

        self.addCleanup(user_patcher.stop)
        self.addCleanup(auth_patcher.stop)

    @freeze_time("2017-11-24 21:01:01")
    @httpretty.activate
    @patch('fbtimer.util.get_local_tz')
    def test_show_timer___running(self, mock_tz):
        mock_tz.return_value = tz.tzutc()
        httpretty.register_uri(
            httpretty.GET, 'https://api.freshbooks.com/timetracking/business/123/timers',
            body=json.dumps(get_fixture('timer')),
            status=200
        )

        runner = CliRunner()
        result = runner.invoke(cli, ['show'])
        self.assertTrue(self.mock_user.called)
        self.assertEqual(httpretty.last_request().method, "GET")
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Running: 0:03:55, started at 8:57 PM\n')

    @freeze_time("2017-11-24 21:01:01")
    @httpretty.activate
    @patch('fbtimer.util.get_local_tz')
    def test_show_timer___paused(self, mock_tz):
        mock_tz.return_value = tz.tzutc()

        timer = get_fixture('timer')
        timer['timers'][0]['is_running'] = False
        httpretty.register_uri(
            httpretty.GET, 'https://api.freshbooks.com/timetracking/business/123/timers',
            body=json.dumps(timer),
            status=200
        )

        runner = CliRunner()
        result = runner.invoke(cli, ['show'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Paused: 0:03:55, started at 8:57 PM\n')

    @freeze_time("2017-11-24 21:01:01")
    @httpretty.activate
    def test_show_timer___no_timer(self):
        httpretty.register_uri(
            httpretty.GET, 'https://api.freshbooks.com/timetracking/business/123/timers',
            body='{"timers": []}',
            status=200
        )

        runner = CliRunner()
        result = runner.invoke(cli, ['show'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'No running timer\n')

    @freeze_time("2017-11-24 21:01:01")
    @httpretty.activate
    @patch('fbtimer.util.get_local_tz')
    def test_start_timer(self, mock_tz):
        mock_tz.return_value = tz.tzutc()
        httpretty.register_uri(
            httpretty.GET, 'https://api.freshbooks.com/timetracking/business/123/timers',
            body='{"timers": []}',
            status=200
        )
        httpretty.register_uri(
            httpretty.POST, 'https://api.freshbooks.com/timetracking/business/123/time_entries',
            body=json.dumps(get_fixture('time_entry')),
            status=200
        )

        runner = CliRunner()
        result = runner.invoke(cli, ['start'])
        post_body = json.loads(httpretty.last_request().body.decode('utf-8'))

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.output,
            'Timer started at 8:57 PM\n'
        )
        self.assertEqual(httpretty.last_request().method, 'POST')
        self.assertDictEqual(
            post_body,
            {'time_entry': {'is_logged': False, 'started_at': '2017-11-24T21:01:01Z'}}
        )

    @freeze_time("2017-11-24 21:01:01")
    @httpretty.activate
    @patch('fbtimer.util.get_local_tz')
    def test_start_timer___running_timer(self, mock_tz):
        mock_tz.return_value = tz.tzutc()
        httpretty.register_uri(
            httpretty.GET, 'https://api.freshbooks.com/timetracking/business/123/timers',
            body=json.dumps(get_fixture('timer')),
            status=200
        )

        runner = CliRunner()
        result = runner.invoke(cli, ['start'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(httpretty.last_request().method, 'GET')
        self.assertEqual(result.output, 'You already have a timer running\n')

    @freeze_time("2017-11-24 21:01:01")
    @httpretty.activate
    @patch('fbtimer.util.get_local_tz')
    def test_discard_timer(self, mock_tz):
        mock_tz.return_value = tz.tzutc()
        httpretty.register_uri(
            httpretty.GET, 'https://api.freshbooks.com/timetracking/business/123/timers',
            body=json.dumps(get_fixture('timer')),
            status=200
        )
        httpretty.register_uri(
            httpretty.DELETE, 'https://api.freshbooks.com/timetracking/business/123/timers/123456',
            body=json.dumps(get_fixture('time_entry')),
            status=204
        )

        runner = CliRunner()
        result = runner.invoke(cli, ['discard'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(httpretty.last_request().method, 'DELETE')
        self.assertEqual(result.output, 'Discarding timer\n')

    @freeze_time("2017-11-24 21:01:01")
    @httpretty.activate
    @patch('fbtimer.util.get_local_tz')
    def test_pause_timer(self, mock_tz):
        mock_tz.return_value = tz.tzutc()

        timer = get_fixture('timer')
        httpretty.register_uri(
            httpretty.GET, 'https://api.freshbooks.com/timetracking/business/123/timers',
            body=json.dumps(get_fixture('timer')),
            status=200
        )

        timer['timers'][0]['is_running'] = False
        httpretty.register_uri(
            httpretty.PUT, 'https://api.freshbooks.com/timetracking/business/123/time_entries/654321',
            body=json.dumps(timer),
            status=200
        )

        runner = CliRunner()
        result = runner.invoke(cli, ['pause'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(httpretty.last_request().method, 'PUT')
        self.assertEqual(result.output, 'Timer paused\n')

    @freeze_time("2017-11-24 21:01:01")
    @httpretty.activate
    def test_pause_timer___no_running_timer(self):
        httpretty.register_uri(
            httpretty.GET, 'https://api.freshbooks.com/timetracking/business/123/timers',
            body='{"timers": []}',
            status=200
        )

        runner = CliRunner()
        result = runner.invoke(cli, ['pause'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(httpretty.last_request().method, 'GET')
        self.assertEqual(result.output, 'There is no timer running\n')
