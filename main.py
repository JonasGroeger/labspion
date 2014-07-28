#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import logging

import trollius as asyncio

import client


__author__ = u'Jonas Gröger <jonas.groeger@gmail.com>'

logging.basicConfig()
logging.getLogger(__name__).setLevel(logging.DEBUG)


def main():
    hostnames = {
        '00:87:40:8F:77:C6': u'Jonas Gröger Raspberry Pi',
        '8C:70:5A:7A:2F:50': u'Jonas Gröger Laptop',
        '10:68:3F:FA:4D:2D': u'Jonas Gröger Handy',
        'BC:F5:AC:F8:D2:0C': u'Sebastian Hof Handy',
        '54:26:96:CD:C0:6F': u'Sebastian Hof Laptop',
    }
    conf = client.Configuration('labspion.ini', 'labspion')
    database = client.Database('labspion.db')
    router = client.Router({'login': conf.login_url(),
                            'devices': conf.devices_url()}, auth=conf.auth(), hostnames=hostnames)
    labspion = client.Labspion(database, router)

    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(labspion.run()),
        loop.create_task(database.truncate()),
    ]
    try:
        loop.run_until_complete(asyncio.wait(tasks))
    finally:
        loop.close()


if __name__ == '__main__':
    main()
