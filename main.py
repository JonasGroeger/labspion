#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import logging
import sys

from labspion import client


__author__ = u'Jonas Gröger <jonas.groeger@gmail.com>'

logging.basicConfig(
    stream=sys.stdout,
    format='%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger('labspion')


def main():
    hostnames = {
        '00:87:40:8F:77:C6': u'Jonas Gröger Raspberry Pi',
        '10:68:3F:FA:4D:2D': u'Jonas Gröger Handy',
        '54:26:96:CD:C0:6F': u'Sebastian Hof Laptop',
        '68:17:29:A0:26:39': u'Matthias Hafner Laptop',
        '8C:70:5A:7A:2F:50': u'Jonas Gröger Laptop',
        'BC:F5:AC:F8:D2:0C': u'Sebastian Hof Handy',
    }
    conf = client.Configuration('labspion.ini', 'labspion')
    database = client.Database('database/labspion.db')

    # We select the router
    router = client.DDWRT(conf, hostnames=hostnames)

    labspion = client.Labspion(database, router)
    labspion.run()


if __name__ == '__main__':
    main()
