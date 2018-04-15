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
    UPDATE_TEXT = 'Update:\n1. Client\n2. Project\n3. Service\n4. Note\n0. Quit\n'
    RECENT_CLIENTS_TEXT = (
        'Recent Clients:\n'
        '1. Internal (My Business)\n'
        '2. American Cyanamid (Gordon Shumway)\n'
        '3. William Tanner\n'
        '0. Go back\n'
    )

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

    @httpretty.activate
    @patch('fbtimer.cli.save_details')
    def test_start_timer__with_details(self, mock_details):
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
        result = runner.invoke(cli, ['start', '-d'])

        self.assertEqual(result.exit_code, 0)
        self.assertTrue(mock_details.called)

    @httpretty.activate
    def test_details__prompts_client_if_none(self):
        httpretty.register_uri(
            httpretty.GET, 'https://api.freshbooks.com/timetracking/business/123/timers',
            body=json.dumps(get_fixture('timer')),
            status=200
        )
        httpretty.register_uri(
            httpretty.GET, 'https://api.freshbooks.com/accounting/account/abc/users/clients'
            '?page=1&per_page=5&search[vis_state]=0&sort=updated_desc',
            body=json.dumps(get_fixture('clients')),
            status=200
        )

        runner = CliRunner()
        result = runner.invoke(cli, ['details'], input='0')

        self.assertEqual(httpretty.last_request().method, "GET")
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.output,
            'Recent Clients:\n'
            '1. Internal (My Business)\n'
            '2. American Cyanamid (Gordon Shumway)\n'
            '3. William Tanner\n'
            '0. Go back\n'
        )

    @httpretty.activate
    def test_details__pick_client(self):
        timer = get_fixture('timer')
        httpretty.register_uri(
            httpretty.GET, 'https://api.freshbooks.com/timetracking/business/123/timers',
            body=json.dumps(timer),
            status=200
        )
        timer['timers'][0]['time_entries'][0]['client_id'] = 123
        httpretty.register_uri(
            httpretty.PUT, 'https://api.freshbooks.com/timetracking/business/123/time_entries/654321',
            body=json.dumps(timer),
            status=200
        )
        httpretty.register_uri(
            httpretty.GET, 'https://api.freshbooks.com/accounting/account/abc/users/clients'
            '?page=1&per_page=5&search[vis_state]=0&sort=updated_desc',
            body=json.dumps(get_fixture('clients')),
            status=200
        )

        runner = CliRunner()
        result = runner.invoke(cli, ['details'], input='2')

        self.assertEqual(httpretty.last_request().method, "GET")
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.output,
            ''.join([
                self.RECENT_CLIENTS_TEXT,
                'Setting client to American Cyanamid (Gordon Shumway)\n'
            ])
        )

    @httpretty.activate
    def test_details__change_client(self):
        timer = get_fixture('timer')
        timer['timers'][0]['time_entries'][0]['client_id'] = 123
        httpretty.register_uri(
            httpretty.GET, 'https://api.freshbooks.com/timetracking/business/123/timers',
            body=json.dumps(timer),
            status=200
        )
        timer['timers'][0]['time_entries'][0]['client_id'] = 456
        httpretty.register_uri(
            httpretty.PUT, 'https://api.freshbooks.com/timetracking/business/123/time_entries/654321',
            body=json.dumps(timer),
            status=200
        )
        httpretty.register_uri(
            httpretty.GET, 'https://api.freshbooks.com/accounting/account/abc/users/clients'
            '?page=1&per_page=5&search[vis_state]=0&sort=updated_desc',
            body=json.dumps(get_fixture('clients')),
            status=200
        )

        runner = CliRunner()
        result = runner.invoke(cli, ['details'], input='1\n3\n0\n')

        self.assertEqual(httpretty.last_request().method, "PUT")
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.output,
            ''.join([
                self.UPDATE_TEXT,
                self.RECENT_CLIENTS_TEXT,
                self.RECENT_CLIENTS_TEXT,
                'Setting client to William Tanner\n',
                self.UPDATE_TEXT,
                self.UPDATE_TEXT,
            ])
        )

    @httpretty.activate
    def test_details__internal_client(self):
        timer = get_fixture('timer')
        httpretty.register_uri(
            httpretty.GET, 'https://api.freshbooks.com/timetracking/business/123/timers',
            body=json.dumps(timer),
            status=200
        )
        timer['timers'][0]['time_entries'][0]['internal'] = True
        httpretty.register_uri(
            httpretty.PUT, 'https://api.freshbooks.com/timetracking/business/123/time_entries/654321',
            body=json.dumps(timer),
            status=200
        )
        httpretty.register_uri(
            httpretty.GET, 'https://api.freshbooks.com/accounting/account/abc/users/clients'
            '?page=1&per_page=5&search[vis_state]=0&sort=updated_desc',
            body=json.dumps(get_fixture('clients')),
            status=200
        )

        runner = CliRunner()
        result = runner.invoke(cli, ['details'], input='1\n0\n')

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.output,
            ''.join([
                self.RECENT_CLIENTS_TEXT,
                'Setting client to Internal (My Business)\n'
            ])
        )