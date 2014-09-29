# -*- coding: utf-8 -*-
import time

import humanize


__author__ = u'Jonas Gröger <jonas.groeger@gmail.com>'


def seconds_ago(ago):
    return humanize.naturaltime(time.time() - ago)


def groupn(l, n):
    return map(list, zip(*(iter(l),) * n))
