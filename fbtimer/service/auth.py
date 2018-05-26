import logging
import os

import click
from requests_oauthlib import OAuth2Session

from fbtimer import FRESHBOOKS_BASE_URL
from fbtimer.service.config import write_token


log = logging.getLogger(__name__)

CLIENT_ID = '503203a5111a38c1af565068dcaca80f56ca1c6983c6ed7c39d374bc67d42179'
CLIENT_SECRET = '24c720272db55588895944729d562ca5baff2e1ced7039724dfeb5500fc311fa'


FRESHBOOKS_TOKEN_URL = 'auth/oauth/token'


def auth(token, include_content_type=True):
    extra = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    client = OAuth2Session(
        CLIENT_ID,
        token=token,
        auto_refresh_url='{}{}'.format(FRESHBOOKS_BASE_URL, FRESHBOOKS_TOKEN_URL),
        auto_refresh_kwargs=extra,
        token_updater=write_token
    )
    client.headers.update(fb_headers(include_content_type))
    return client


def authorize():
    redirect_uri = 'https://amcintosh.net/fbtimer/'
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=redirect_uri)
    authorization_url, state = oauth.authorization_url(
        os.getenv('FBTIMER_AUTH_URL', 'https://my.freshbooks.com/service/auth/oauth/authorize'))

    click.secho('First we need access to your FreshBooks account. '
                'Press a key to open your browser and obtain an authorization code',
                fg='blue')
    click.pause()
    click.secho('Please go to {} and authorize access.'.format(authorization_url), fg='blue')
    click.launch(authorization_url)
    authorization_response = click.prompt('Enter the authorization code')

    oauth.headers.update(fb_headers())
    token = oauth.fetch_token(
        token_url='{}{}'.format(FRESHBOOKS_BASE_URL, FRESHBOOKS_TOKEN_URL),
        code=authorization_response,
        client_secret=CLIENT_SECRET,
        token=state
    )
    write_token(token)
    return token


def fb_headers(include_content_type=True):
    headers = {
        "Api-Version": "alpha",
    }
    if include_content_type:
        headers["Content-Type"] = "application/json"
    return headers
