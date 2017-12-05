import configparser
import logging
import os
import time

import click

log = logging.getLogger(__name__)


def read_user():
    log.debug('Looking for token in config file')
    config = _get_config()
    try:
        token = {
            'token_type': 'Bearer',
            'access_token': config.get("Auth", "access_token"),
            'refresh_token': config.get("Auth", "refresh_token"),
            'expires_in': float(config.get("Auth", "expires_at")) - time.time()
        }
        business = (
            config.get("Business", "business_name"),
            int(config.get("Business", "business_id")),
            config.get("Business", "account_id")
        )
        return token, business
    except (configparser.NoSectionError, configparser.NoOptionError):
        raise MissingAuthError('No authorization found')


def write_token(token):
    config = _get_config()
    if not config.has_section('Auth'):
        config.add_section('Auth')
    config.set('Auth', 'access_token', token['access_token'])
    config.set('Auth', 'refresh_token', token['refresh_token'])
    config.set('Auth', 'expires_at', str(token['expires_at']))

    _write_config(config)


def write_business(business_name, business_id, account_id):
    config = _get_config()
    if not config.has_section('Business'):
        config.add_section('Business')
    config.set('Business', 'business_name', business_name)
    config.set('Business', 'business_id', str(business_id))
    config.set('Business', 'account_id', account_id)
    _write_config(config)


def _get_config_path():
    return os.path.join(click.get_app_dir('fbtimer'), 'settings.ini')


def _get_config():
    conf_path = _get_config_path()
    config = configparser.ConfigParser()
    config.read(conf_path)
    return config


def _write_config(config):
    conf_path = click.get_app_dir('fbtimer')
    try:
        os.makedirs(conf_path)
    except OSError:
        log.debug('Config directory already exists')

    log.debug('Writing token to "%s"', conf_path)
    conf = open(_get_config_path(), 'w')
    config.write(conf)
    conf.close()


class MissingAuthError(Exception):
    pass
