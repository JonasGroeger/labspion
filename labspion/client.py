# -*- coding: utf-8 -*-
import ConfigParser
import abc
import logging
import sqlite3
import time

import utils


__author__ = u'Jonas Gröger <jonas.groeger@gmail.com>'

logger = logging.getLogger('labspion.client')


class Configuration(object):
    def __init__(self, ini_file, section):
        self.ini_file = ini_file
        self.section = section
        self.config = self._read_config()

    def _read_config(self):
        config = ConfigParser.ConfigParser()
        if not config.read(self.ini_file):
            raise IOError('Could not find configuration file "{}".'.format(self.ini_file))
        return config

    def internal(self):
        return self.config.get(self.section, 'internal') + self.page()

    def external(self):
        return self.config.get(self.section, 'external') + self.page()

    def page(self):
        return self.config.get(self.section, 'page')

    def username(self):
        return self.config.get(self.section, 'username')

    def password(self):
        return self.config.get(self.section, 'password')

    def auth(self):
        return self.username(), self.password()


class Database(object):
    def __init__(self, filename):
        self.filename = filename
        self.connection = None
        self.cursor = None

    def open(self):
        if not all([self.connection, self.cursor]):
            self.connection = sqlite3.connect(self.filename)
            self.cursor = self.connection.cursor()
        return self.connection, self.cursor

    def close(self):
        self.cursor.close()
        self.cursor = None
        self.connection.close()
        self.connection = None

    def insert(self, clients_json):
        self.open()
        self.cursor.executemany('INSERT INTO labspion VALUES (NULL,?,?,?,?)', clients_json)
        self.connection.commit()
        logger.info('Inserted {} clients into DB.'.format(len(clients_json)))

    def clients(self):
        self.open()
        sql = 'SELECT l.mac, l.ipv4, max(l.seen) AS seen, l.hostname FROM labspion AS l GROUP BY l.mac'
        clients = self.cursor.execute(sql)
        clients_json = [{'mac': c[0], 'ipv4': c[1], 'seen': utils.seconds_ago(c[2]), 'hostname': c[3]} for c in
                        clients]
        logger.info('Returned {} clients to caller.'.format(len(clients_json)))
        return clients_json

    def truncate(self):
        self.open()
        self.connection.execute('DELETE FROM labspion')
        self.connection.execute('DELETE FROM SQLITE_SEQUENCE WHERE name="labspion"')
        self.connection.commit()
        logger.info('Truncated "{}".'.format(self.filename))


class Labspion(object):
    def __init__(self, database, router):
        self.database = database
        self.router = router

    @staticmethod
    def _database_tuple(clients_dict):
        return [(c['mac'], c['ipv4'], c['seen'], c['hostname']) for c in clients_dict]

    def run(self):
        while True:
            clients_dict = self.router.clients()

            # We need to make sure the order is right
            clients_tuple = Labspion._database_tuple(clients_dict)

            self.database.insert(clients_tuple)
            logger.debug('Labspion is sleeping for 10 seconds.')
            time.sleep(10)


class Router(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def clients(self):
        """Retrieve a list of all clients logged in a router. Each element contains mac, ipv4, seen and a hostname."""
        return


