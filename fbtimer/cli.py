import click
import logging
import os
from datetime import timedelta
import fbtimer
from fbtimer.model.user import User
from fbtimer.service.timer import get_timer
from fbtimer.service.time_entry import create_new_time_entry
import requests
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
@click.version_option(version=fbtimer.__version__)
@click.pass_context
def cli(ctx, verbose, stdout):
    configure_logging(verbose, stdout)
    if ctx.invoked_subcommand is None:
        ctx.invoke(show)


@cli.command()
def show():
    '''Show any currently running timers. The default command.'''
    timer = get_timer(User())

    if not timer:
        click.secho('No running timer', fg='blue')
        return
    if timer.is_running:
        click.secho(
            'Running: {}, started at {}'.format(
                timedelta(seconds=timer.duration), timer.start_time.strftime('%I:%M %p')),
            fg='green'
        )
    else:
        click.secho(
            'Paused: {}, started at {}'.format(
                timedelta(seconds=timer.duration), timer.start_time.strftime('%I:%M %p')),
            fg='magenta'
        )


@cli.command()
def start():
    '''Shart or resume timers.'''
    user = User()
    timer = get_timer(user)

    if timer and timer.is_running:
        pass  # fail
    else:
        try:
            timer = create_new_time_entry(user)
            click.secho(
            'Timer started at {}'.format(
                parse_datetime_to_local(timer['time_entry'].get('started_at')).strftime('%I:%M %p')),
            fg='green'
        )

        except requests.exceptions.HTTPError as e:
            click.secho('Error while trying to start timer', fg='magenta')
            log.debug(e)


@cli.command()
def logout():
    '''Log out and delete any authorization data.'''
    os.remove(os.path.join(click.get_app_dir('fbtimer'), 'settings.ini'))
