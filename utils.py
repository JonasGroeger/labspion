#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import time
import datetime

import humanize
import pytz


__author__ = u'Jonas Gröger <jonas.groeger@gmail.com>'


def seconds_ago(ago):
    return humanize.naturaltime(time.time() - ago)


def seconds_until_hour(hours):
    tz = pytz.timezone('Europe/Berlin')
    tomorrow_4am = datetime.datetime.replace(datetime.datetime.now(tz) + datetime.timedelta(days=1), hour=hours, minute=0,
                                             second=0)
    return (tomorrow_4am - datetime.datetime.now(tz)).seconds