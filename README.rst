FreshBooks-Timer
================

Installation and Requirements
-----------------------------

FreshBooks-Timer has been written for Python 3.3+.

To install (either from PyPI or source):

::

    $ pip install fbtimer

or from source:

::

    $ python setup.py install

Usage
-----

To get started, run fbtimer and follow the steps to authorize it against
your FreshBooks acocunt.

::

    $ fbtimer

Usage:

::

    Usage: fbtimer [OPTIONS] COMMAND [ARGS]...

    Options:
      -o, --stdout   Enable logging to stdout. Helpful for debugging.
      -v, --verbose  Enable debug logging.
      --version      Show the version and exit.
      --help         Show this message and exit.

    Commands:
      details  Update timer details
      discard  Stop and delete the current timer
      log      Stop the timer and log it
      logout   Log out and delete any authorization data.
      pause    Pause current timer.
      show     Show any currently running timers.
      start    Start or resume timers.
