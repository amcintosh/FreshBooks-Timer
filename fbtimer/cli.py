import logging
import os

import click
import requests

from fbtimer import __version__
from fbtimer.model.user import User
from fbtimer.service.client import get_recent_clients
from fbtimer.service.time_entry import (
    create_new_time_entry, pause_time_entry, update_time_entry
)
from fbtimer.service.timer import get_timer, delete_timer, log_timer
from fbtimer.util import parse_datetime_to_local

log = logging.getLogger(__name__)


def configure_logging(verbose, stdout):
    if stdout and verbose:
        logging.basicConfig(format='%(levelname)s (%(filename)s:%(lineno)d): %(message)s',
                            level=logging.DEBUG)
    elif stdout:
        logging.basicConfig(format='%(message)s',
                            level=logging.INFO)


@click.group(invoke_without_command=True)
@click.option('-o', '--stdout', is_flag=True, help='Enable logging to stdout. Helpful for debugging.')
@click.option('-v', '--verbose', is_flag=True, help='Enable debug logging.')
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, verbose, stdout):
    configure_logging(verbose, stdout)
    if ctx.invoked_subcommand is None:
        ctx.invoke(show)


@cli.command()
def logout():
    '''Log out and delete any authorization data.'''
    os.remove(os.path.join(click.get_app_dir('fbtimer'), 'settings.ini'))


@cli.command()
def show():
    '''Show any currently running timers. The default command.'''
    timer = get_timer(User())

    if not timer:
        click.secho('No running timer', fg='blue')
        return
    if timer.is_running:
        click.secho(str(timer), fg='green')
    else:
        click.secho(str(timer), fg='magenta')


@cli.command()
@click.option('-d', '--details', is_flag=True, help='Fill out timer details when started.')
@click.pass_context
def start(ctx, details):
    '''Start or resume timers.'''
    user = User()
    timer = get_timer(user)

    if timer and timer.is_running:
        click.secho('You already have a timer running', fg='magenta')
        return

    try:
        timer = create_new_time_entry(user, timer)
        click.secho(
            'Timer started at {}'.format(
                parse_datetime_to_local(timer['time_entry'].get('started_at')).strftime('%-I:%M %p')),
            fg='green'
        )
        if details:
            ctx.invoke(save_details)

    except requests.exceptions.HTTPError as e:
        click.secho('Error while trying to start timer', fg='magenta')
        log.debug(e)


@cli.command()
def pause():
    '''Pause current timer.'''
    user = User()
    timer = get_timer(user)

    if not timer or not timer.is_running:
        click.secho('There is no timer running', fg='magenta')
        return
    timer = pause_time_entry(user, timer)
    click.secho('Timer paused', fg='green')


@cli.command()
def discard():
    '''Stop and delete the current timer'''
    user = User()
    timer = get_timer(user)
    click.secho('Discarding timer', fg='green')
    if not timer:
        return
    try:
        delete_timer(user, timer)
    except requests.exceptions.HTTPError as e:
        click.secho('Error while trying to delete timer', fg='magenta')
        log.debug(e)


@cli.command('log')
def log_time():
    '''Stop the timer and log it'''
    user = User()
    timer = get_timer(user)

    if not timer:
        click.secho('There is no timer to log', fg='magenta')
        return
    try:
        log_timer(user, timer)
        click.secho('Your time has been logged', fg='green')
    except requests.exceptions.HTTPError as e:
        click.secho('Error while trying to log timer', fg='magenta')
        log.debug(e)


@cli.command('details')
@click.pass_context
def save_details(ctx):
    '''Update timer details'''
    user = User()
    timer = get_timer(user)
    if not timer or not timer.is_running:
        click.secho('There is no timer running', fg='magenta')
        return

    if not timer.has_client:
        choose_client(ctx, user, timer)
        timer = get_timer(user)

    choice = None
    while choice != '0' and timer.has_client:
        click.secho('Update:', fg='green')
        click.secho('1. Client', fg='blue')
        click.secho('2. Project', fg='blue')
        click.secho('3. Service', fg='blue')
        click.secho('4. Note', fg='blue')
        click.secho('0. Quit', fg='blue')
        choice = click.getchar()

        if choice == '1':
            choose_client(ctx, user, timer)
        elif choice in ['2', '3', '4']:
            update_not_implemented()


def choose_client(ctx, user, timer):
    clients = get_recent_clients(user)

    click.secho('Recent Clients:', fg='green')
    click.secho('1. Internal ({})'.format(user.business_name), fg='blue')
    for idx, client in enumerate(clients):
        click.secho('{}. {}'.format(idx+2, client), fg='blue')
    click.secho('0. Go back', fg='blue')

    choice = click.getchar()

    if choice == '0':
        return
    if choice == '1':
        update_time_entry(user, timer, internal_client=True)
        click.secho('Setting client to Internal ({})'.format(user.business_name), fg='green')
        return
    try:
        selected = clients[int(choice) - 2]
        update_time_entry(user, timer, client_id=selected.id)
        click.secho('Setting client to {}'.format(selected), fg='green')
    except requests.exceptions.HTTPError as e:
        click.secho('Error while trying to update timer', fg='magenta')
        log.debug(e)
    except Exception as e:
        log.debug(e)
        choose_client(ctx, user, timer)


def update_not_implemented():
    click.secho('Not yet implemented', fg='green')
    click.secho(
        'Go to https://my.freshbooks.com/#/time-tracking to fill out the details.',
        fg='green'
    )
