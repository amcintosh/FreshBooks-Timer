import logging
import os

import click
import requests

from fbtimer import __version__
from fbtimer.model.user import User
from fbtimer.service.time_entry import create_new_time_entry, pause_time_entry
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
def start():
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
        click.secho(
            'Go to https://my.freshbooks.com/#/time-tracking to fill out the details.',
            fg='green'
        )

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
        timer = delete_timer(user, timer)
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
        # Do PUT to /timers with full payload (all time_entries)
        # each with duration and is_logged = true
        timer = log_timer(user, timer)
        click.secho('Your time has been logged', fg='green')
    except requests.exceptions.HTTPError as e:
        click.secho('Error while trying to log timer', fg='magenta')
        log.debug(e)
