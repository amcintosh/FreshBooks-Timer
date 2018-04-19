FreshBooks-Timer
================

|Build Status| |codecov|

Track time in FreshBooks via the command line.

Installation and Requirements
-----------------------------

FreshBooks-Timer has been written for Python 2.7 and 3.3+.

To install (either from PyPI or source):

::

    $ pip install fbtimer

or from source:

::

    $ python setup.py install

Usage
-----

Getting Started
~~~~~~~~~~~~~~~

To get started, run ``fbtimer`` and follow the steps to authorize it
against your FreshBooks account.

::

    $ fbtimer

    First we need access to your FreshBooks account. Press a key to open your browser and obtain an authorization code
    Press any key to continue ...

This should open your browser and send you to FreshBooks to authorize.
If not, we'll prin the URL for you to go to. After authorizing, you will
be directed to a page showing you the authorization code needed in the
next step:

::

    Please go to <FreshBooks auth URL> and authorize access.
    Enter the authorization code:

Commands
~~~~~~~~

::

    $ fbtimer --help

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

    $ fbtimer start --help

    Usage: fbtimer start [OPTIONS]

      Start or resume timers.

    Options:
      -d, --details  Fill out timer details when started.
      --help         Show this message and exit.

Usage Examples
~~~~~~~~~~~~~~

Logging Time
^^^^^^^^^^^^

::

    # fbtimer
    No running timer

    # fbtimer start
    Timer started at 2:50 PM

Do some work. And when you're ready to log:

::

    $ fbtimer
    Running: 0:25:39, started at 2:50 PM

    $ fbtimer details
    Recent Clients:
    1. Internal (My Business)
    2. Gordon Shumway
    3. William Tanner
    0. Go back

    $ 1
    Setting client to Date Dude
    Update:
    1. Client
    2. Project
    3. Service
    4. Note
    0. Quit

    $ 0
    $ fbtimer log
    Your time has been logged

Setting details right away
^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    # fbtimer start -d
    Timer started at 2:50 PM
    Recent Clients:
    1. Internal (FreshBooks)
    2. Jenn Kim
    3. Date Dude
    4. lolpdf (PDF Man)
    0. Go back

Take a break
^^^^^^^^^^^^

::

    $ fbtimer pause
    Timer paused

    $ fbtimer
    Paused: 0:15:43, started at 2:50 PM

    $ fbtimer start   // To resume
    Timer started at 3:26 PM

Never mind
^^^^^^^^^^

::

    $ fbtimer
    Running: 0:25:39, started at 2:50 PM

    $ fbtimer discard
    Discarding timer

    $ fbtimer show   // Same as fbtimer
    No running timer

.. |Build Status| image:: https://travis-ci.org/amcintosh/FreshBooks-Timer.svg?branch=master
   :target: https://travis-ci.org/amcintosh/FreshBooks-Timer
.. |codecov| image:: https://codecov.io/gh/amcintosh/FreshBooks-Timer/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/amcintosh/FreshBooks-Timer
