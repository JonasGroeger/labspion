#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import codecs
import json
import logging
import sys

from labspion import client
from labspion.common import CONFIGURATION_FILE, DATABASE_FILE
from labspion.routers import ddwrt


__author__ = u'Jonas Gröger <jonas.groeger@gmail.com>'

logging.basicConfig(
    stream=sys.stdout,
    format='%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger('labspion')


def main():
    hostnames = json.load(codecs.open('hostnames.txt', encoding="UTF-8"))

    configuration = client.Configuration(CONFIGURATION_FILE, section='labspion')
    database = client.Database(DATABASE_FILE)

    # We select the router
    router = ddwrt.DDWRT(configuration, hostnames=hostnames)

    # Data from router -> database
    labspion = client.Labspion(database, router)
    labspion.run()


if __name__ == '__main__':
    main()
