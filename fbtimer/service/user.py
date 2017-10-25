import click
import os
import configparser
import time
import logging

log = logging.getLogger(__name__)


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
    except (configparser.NoSectionError, configparser.NoOptionError):
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


class MissingAuthError(Exception):
    pass
