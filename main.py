#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import trollius as asyncio

import database
from wifi_clients import active_clients


__author__ = 'Jonas Gröger <jonas.groeger@gmail.com>'


def seconds_until_4am():
    import datetime
    import pytz

    tz = pytz.timezone('Europe/Berlin')
    tomorrow_4am = datetime.datetime.replace(datetime.datetime.now(tz) + datetime.timedelta(days=1), hour=4, minute=0, second=0)
    seconds_until_4am = (tomorrow_4am - datetime.datetime.now(tz)).seconds
    return seconds_until_4am



@asyncio.coroutine
def insert_clients(db):
    while True:
        db.open()
        clients_dict = active_clients()
        clients_tuple = [
            (c['mac'], c['ipv4'], c['seen'], c['hostname']) for c in clients_dict
        ]
        db.insert(clients_tuple)
        db.close()
        yield asyncio.From(asyncio.sleep(10))


@asyncio.coroutine
def clear_db(db):
    while True:
        until_4am = seconds_until_4am()
        yield asyncio.From(asyncio.sleep(until_4am))
        db.open()
        db.truncate()
        db.close()


def main():
    db = database.Database('labspion.db')
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(insert_clients(db)),
        loop.create_task(clear_db(db)),
    ]
    try:
        loop.run_until_complete(asyncio.wait(tasks))
    finally:
        loop.close()


if __name__ == '__main__':
    main()
