#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import logging
import sys

from labspion import client
from labspion.common import CONFIGURATION_FILE, DATABASE_FILE


__author__ = u'Jonas Gröger <jonas.groeger@gmail.com>'

logging.basicConfig(
    stream=sys.stdout,
    format='%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger('labspion')


def main():
    hostnames = {
        '8C:70:5A:7A:2F:50': u'Jonas Gröger Laptop',
        '00:87:40:8F:77:C6': u'Jonas Gröger Raspberry Pi',
        '10:68:3F:FA:4D:2D': u'Jonas Gröger Handy',
        '54:26:96:CD:C0:6F': u'Sebastian Hof Laptop',
        'BC:F5:AC:F8:D2:0C': u'Sebastian Hof Handy',
        '68:17:29:A0:26:39': u'Matthias Hafner Laptop',
    }

    configuration = client.Configuration(CONFIGURATION_FILE, section='labspion')
    database = client.Database(DATABASE_FILE)

    # We select the router
    router = client.DDWRT(configuration, hostnames=hostnames)

    # Data from router -> database
    labspion = client.Labspion(database, router)
    labspion.run()


if __name__ == '__main__':
    main()
