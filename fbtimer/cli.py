import click
import logging
import os
from datetime import timedelta
import dateutil.parser
from dateutil import tz
from fbtimer.model.user import User
from fbtimer.service.timer import get_timer

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
@click.pass_context
def cli(ctx, verbose, stdout):
    configure_logging(verbose, stdout)
    if ctx.invoked_subcommand is None:
        ctx.invoke(show)


@cli.command()
def show():
    '''Show any currently running timers. The default command.'''
    user = User()
    data = get_timer(user)
    log.debug(data)

    if len(data.get('timers')) == 0:
        click.secho('No running timer', fg='blue')
        return
    timer = data.get('timers')[0]
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    start_time = dateutil.parser.parse(timer.get('time_entries')[0]['started_at'])
    start_time = start_time.replace(tzinfo=from_zone)
    start_time = start_time.astimezone(to_zone)
    duration = 0
    for time_entry in timer.get('time_entries'):
        if time_entry.get('duration'):
            duration = duration + time_entry.get('duration')
    if timer['is_running']:
        click.secho(
            'Running: {}, started at {}'.format(
                timedelta(seconds=duration), start_time.strftime('%I:%M %p')),
            fg='green'
        )
    else:
        click.secho(
            'Paused: {}, started at {}'.format(
                timedelta(seconds=duration), start_time.strftime('%I:%M %p')),
            fg='magenta'
        )


@cli.command()
def logout():
    '''Log out and delete any authorization data.'''
    os.remove(os.path.join(click.get_app_dir('fbtimer'), 'settings.ini'))
