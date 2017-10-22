import os
from pathlib import Path
import configparser
from requests_oauthlib import OAuth2Session
import time
import logging
import click

log = logging.getLogger(__name__)

CLIENT_ID = '503203a5111a38c1af565068dcaca80f56ca1c6983c6ed7c39d374bc67d42179'
CLIENT_SECRET = '24c720272db55588895944729d562ca5baff2e1ced7039724dfeb5500fc311fa'

FB_TOKEN_URL = 'https://api.freshbooks.com/auth/oauth/token'

def get_token():
    try:
        token = read_token()
    except MissingAuthError:
        token = authorize()
    return token

def make_req(token, url):
    extra = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    client = OAuth2Session(
        CLIENT_ID,
        token=token,
        auto_refresh_url=FB_TOKEN_URL,
        auto_refresh_kwargs=extra,
        token_updater=write_token
    )
    client.headers.update(fb_headers())
    res = client.get(url)
    return res

def read_token():
    conf_path = os.path.join(click.get_app_dir('fbtimer'), 'settings.ini')
    log.debug('Looking for token in "%s"', conf_path)
    config = configparser.ConfigParser()
    config.read(conf_path)
    try:
        token = {
            'token_type': 'Bearer',
            'access_token': config.get("Auth", "access_token"),
            'refresh_token': config.get("Auth", "refresh_token"),
            'expires_in': float(config.get("Auth", "expires_at")) - time.time()
        }
        return token
    except (configparser.NoSectionError, configparser.NoOptionError) as err:
        raise MissingAuthError('No authorization found')

def write_token(token):
    config = configparser.ConfigParser()
    config.add_section('Auth')
    config.set('Auth', 'access_token', token['access_token'])
    config.set('Auth', 'refresh_token', token['refresh_token'])
    config.set('Auth', 'expires_at', str(token['expires_at']))

    conf_path = click.get_app_dir('fbtimer')
    os.makedirs(conf_path, exist_ok=True)

    log.debug('Writing token to "%s"', conf_path)
    conf = open(os.path.join(conf_path, 'settings.ini'), 'w')
    config.write(conf)
    conf.close()


def authorize():
    redirect_uri = 'https://github.com/amcintosh/FreshBooks-Timer'
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=redirect_uri)
    authorization_url, state = oauth.authorization_url(
        'https://my.freshbooks.com/service/auth/oauth/authorize')

    print('Please go to %s and authorize access.' % authorization_url)

    authorization_response = input('Enter the full callback URL: ')

    oauth.headers.update(fb_headers())
    token = oauth.fetch_token(
        token_url=FB_TOKEN_URL,
        authorization_response=authorization_response,
        client_secret=CLIENT_SECRET,
        token=state
    )
    write_token(token)
    return token

def fb_headers():
    return {
        "Api-Version": "alpha",
        "Content-Type": "application/json"
    }


class MissingAuthError(Exception):
    pass

