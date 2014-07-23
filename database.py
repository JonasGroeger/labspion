#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import logging
import os
import sqlite3
import time
import humanize

__author__ = u'Jonas Gröger <jonas.groeger@gmail.com>'

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))


def nicetime(ago):
    return humanize.naturaltime(time.time() - ago)


class Database(object):
    def __init__(self, filename):
        self.filename = filename
        self.connection = None
        self.cursor = None

    def _db_closed(self, action):
        if not all([self.connection, self.cursor]):
            logging.warn('Trying to "{}" but connection or cursor is closed.'.format(action))
            return True
        return False

    def open(self):
        self.connection = sqlite3.connect(self.filename)
        self.cursor = self.connection.cursor()
        return self.connection, self.cursor

    def close(self):
        self.cursor.close()
        self.connection.close()

    def insert(self, clients_json):
        if self._db_closed('insert'):
            return
        self.cursor.executemany('INSERT INTO labspion VALUES (NULL ,?,?,?,?)', clients_json)
        self.connection.commit()

    def clients(self):
        self.open()
        clients = self.cursor.execute('SELECT l.mac, l.ipv4, l.seen, l.hostname FROM labspion AS l')
        clients_json = [{'mac': c[0], 'ipv4': c[1], 'seen': nicetime(c[2]), 'hostname': c[3]} for c in
                        clients]
        self.close()
        return clients_json

    def truncate(self):
        if self._db_closed('truncate'):
            return
        self.connection.execute('DELETE FROM labspion')
        self.connection.execute('DELETE FROM SQLITE_SEQUENCE WHERE name="labspion"')
        self.connection.commit()
