#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Determines if a datetime is within a given time period. This is a Python
version of Perl's Time::Period module.
"""

from __future__ import print_function

from datetime import datetime
import re

__all__ = ['in_period', 'InvalidFormat']

DAYS = {
    'su': 1,
    'mo': 2,
    'tu': 3,
    'we': 4,
    'th': 5,
    'fr': 6,
    'sa': 7,
}

MONTHS = {
    'jan': 1,
    'feb': 2,
    'mar': 3,
    'apr': 4,
    'may': 5,
    'jun': 6,
    'jul': 7,
    'aug': 8,
    'sep': 9,
    'oct': 10,
    'nov': 11,
    'dec': 12,
}


def in_period(period, dt=None):
    """
    Determines if a datetime is within a certain time period. If the time
    is omitted the current time will be used.

    in_period return True is the datetime is within the time period, False if not.
    If the expression is malformed a TimePeriod.InvalidFormat exception
    will be raised. (Note that this differs from Time::Period, which
    returns -1 if the expression is invalid).

    The format for the time period is like Perl's Time::Period module,
    which is documented in some detail here:

    http://search.cpan.org/~pryan/Period-1.20/Period.pm

    Here's the quick and dirty version.

    Each period is composed of one or more sub-period seperated by a comma.
    A datetime must match at least one of the sub periods to be considered
    in that time period.

    Each sub-period is composed of one or more tests, like so:

        scale {value}

        scale {a-b}

        scale {a b c}

    The datetime must pass each test for a sub-period for the sub-period to
    be considered true.

    For example:

        Match Mondays
        wd {mon}

        Match Monday mornings
        wd {mon} hr {9-16}

        Match Monday morning or Friday afternoon
        wd {mon} hr {0-12}, wd {fri} hr {0-12}

    Valid scales are:
        year
        month
        week
        yday
        mday
        wday
        hour
        minute
        second

    Those can be substituted with their corresponding code:
        yd
        mo
        wk
        yd
        md
        wd
        hr
        min
        sec
    """

    if dt is None:
        dt = datetime.now()

    # transform whatever crazy format we're given and turn it into
    # something like this:
    #
    # md{1}|hr{midnight-noon},md{2}|hr{noon-midnight}
    period = re.sub(r"^\s*|\s*$", '', period)
    period = re.sub(r"\s*(?={|$)", '', period)
    period = re.sub(r",\s*", ',', period)
    period = re.sub(r"\s*-\s*", '-', period)
    period = re.sub(r"{\s*", '{', period)
    period = re.sub(r"\s*}\s*", '}', period)
    period = re.sub(r"}(?=[^,])", '}|', period)
    period = period.lower()

    if period == '':
        return True

    sub_periods = re.split(',', period)

    # go through each sub-period until one matches (OR logic)
    for sp in sub_periods:
        if _is_in_sub_period(sp, dt):
            return True

    return False


def _is_in_sub_period(sp, dt):
    if sp == 'never':
        return 0
    if sp == 'none' or sp == 'always' or sp == '':
        return 1
    scales = sp.split('|')
    range_lists = {}

    # build a list for every scale of ranges
    for scale_exp in scales:
        scale, ranges = _parse_scale(scale_exp)

        # if there's already a list for this scale, add the new ranges to the end
        if scale in range_lists:
            range_lists[scale] += ranges
        else:
            range_lists[scale] = ranges

    # check each scale, if there's a false one return false (AND logic)
    for scale in range_lists:
        result = SCALES[scale](range_lists[scale], dt)
        if result != 1:
            return result

    return 1


def _parse_scale(scale_exp):
    """Parses a scale expression and returns the scale, and a list of ranges."""

    m = re.search("(\w+?)\{(.*?)\}", scale_exp)
    if m is None:
        raise InvalidFormat('Unable to parse the given time period.')
    scale = m.group(1)
    range = m.group(2)

    if scale not in SCALES:
        raise InvalidFormat('%s is not a valid scale.' % scale)

    ranges = re.split("\s", range)

    return scale, ranges


def yr(ranges, dt):

    def normal_year(year, dt):
        if year is None:
            return year

        try:
            year = int(year)
        except ValueError:
            raise InvalidFormat('An integer value is required for year.')

        if year < 100:
            century = dt.year / 100
            year = 100 * century + year

        return year

    for range in ranges:
        low, high = _splitrange(range)
        low = normal_year(low, dt)
        high = normal_year(high, dt)

        if _is_in_range(dt.year, low, high):
            return 1

    return 0


def mo(ranges, dt):
    for range in ranges:
        for month in MONTHS.keys():
            range = re.sub("%s.*?(?=\s|-|$)" % month, str(MONTHS[month]), range)

        low, high = _splitrange(range)
        low, high = _in_min_max(low, high, 1, 12, 'month')

        if _is_in_range(dt.month, low, high):
            return 1

    return 0


def wk(ranges, dt):
    week = (dt.day - 1) / 7 + 1
    return _simple_test(week, ranges, 1, 5, 'week')


def yd(ranges, dt):
    today = int(dt.strftime('%j'))
    return _simple_test(today, ranges, 1, 366, 'year day')


def md(ranges, dt):
    return _simple_test(dt.day, ranges, 1, 31, 'day')


def wd(ranges, dt):
    today = (dt.weekday() + 2) % 7
    # saturday needs to be 7 not zero
    if today == 0:
        today = 7

    for range in ranges:
        # translate days into numbers
        for day in DAYS.keys():
            range = re.sub("%s.*?(?=\s|-|$)" % day, str(DAYS[day]), range)

        low, high = _splitrange(range)
        low, high = _in_min_max(low, high, 1, 7, 'weekday')

        if _is_in_range(today, low, high):
            return 1
    return 0


def hr(ranges, dt):
    now = dt.hour

    def normal_hour(hour):
        if hour is None:
            return None
        try:
            hour = int(hour)
        except ValueError:
            raise InvalidFormat('An integer value is required for hour.')

        return hour

    for range in ranges:
        low, high = _splitrange(range)
        low = normal_hour(low)
        high = normal_hour(high)

        low, high = _in_min_max(low, high, 0, 23, 'hour')
        if _is_in_range(now, low, high):
            return 1

    return 0


def min(ranges, dt):
    return _simple_test(dt.minute, ranges, 0, 59, 'minute')


def sec(ranges, dt):
    return _simple_test(dt.second, ranges, 0, 59, 'second')


def _simple_test(now, ranges, min, max, scale):
    for range in ranges:
        low, high = _splitrange(range)
        low, high = _in_min_max(low, high, min, max, scale)

        if _is_in_range(now, low, high):
            return 1

    return 0


def _splitrange(range):
    lowhigh = range.split('-')
    low = lowhigh[0]
    high = None
    if len(lowhigh) > 1:
        high = lowhigh[1]

    return low, high


def _in_min_max(low, high, min, max, scale):
    try:
        low = int(low)
    except ValueError:
        raise InvalidFormat('An integer value is required for %s.' % scale)

    if low < min or low > max:
        raise InvalidFormat('%d is not valid for %s. Valid options are between %d and %d.' % (low, scale, min, max))
    if high is not None:
        try:
            high = int(high)
        except ValueError:
            raise InvalidFormat('An integer value is required for %s.' % scale)

        if high < min or high > max:
            raise InvalidFormat('%d is not valid for %s. Valid options are between %d and %d.' % (high, scale, min, max))

    return low, high


def _is_in_range(x, low, high):
    if high is None or low == high:
        # just one number
        if low != x:
            return 0
    elif high > low:
        # e.g. mon-fri
        if x > high or x < low:
            return 0
    elif low > high:
        # e.g. fri-mon
        if not (x >= low or x <= high):
            return 0

    return 1


class InvalidFormat(Exception):

    pass


# dict of scale codes with the functions to process them
SCALES = {
    'yr': yr,
    'year': yr,
    'mo': mo,
    'month': mo,
    'wk': wk,
    'week': wk,
    'yd': yd,
    'yday': yd,
    'md': md,
    'mday': md,
    'wd': wd,
    'wday': wd,
    'hr': hr,
    'hour': hr,
    'min': min,
    'minute': min,
    'sec': sec,
    'second': sec,
}

if __name__ == '__main__':
    try:
        print(in_period('md {1}', datetime(2007, 6, 1, 14)))
        print(in_period('hr {9-16}', datetime(2014, 2, 11, 12, 5)))
        print(in_period('', datetime(2014, 2, 10)))
        print(in_period('hr {0-8}', datetime(2014, 2, 11, 12, 6)))
    except InvalidFormat as ife:
        print('Invalid time period format: %s' % ife)
