===========
Time Period
===========

Python module for determining if a datetime is within a time
period.

Based on the `original TimePeriod module`_ written by Paul Boyd <boyd.paul2@gmail.com>.


Installation
============

.. code-block:: bash

    $ sudo pip install timeperiod2

Usage
=====

.. code-block:: python

    import datetime
    import timeperiod
    # will return True iff we have Monday, Tuesday or Thursday:
    timeperiod.in_period('wd {mon tue thu}')
    # will return True iff we have "office time"
    timeperiod.in_period('wd {Mon-Fri} hr {9-17}', datetime.datetime.now())

License
=======

Released under the LGPL:

http://www.gnu.org/licenses/#LGPL

Also see the LICENSE file.

.. _original TimePeriod module: https://pypi.python.org/pypi/TimePeriod
