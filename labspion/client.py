#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import ConfigParser
import abc
import logging
import sqlite3
import time

import requests

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

    def _db_closed(self, action):
        if not all([self.connection, self.cursor]):
            logger.warn('Trying to "{}" but connection or cursor is closed.'.format(action))
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
            self.open()
        self.cursor.executemany('INSERT INTO labspion VALUES (NULL ,?,?,?,?)', clients_json)
        self.connection.commit()
        logger.debug('Inserted {} clients into DB.'.format(len(clients_json)))

    def clients(self):
        self.open()
        sql = 'SELECT l.mac, l.ipv4, max(l.seen) AS seen, l.hostname FROM labspion AS l GROUP BY l.mac'
        clients = self.cursor.execute(sql)
        clients_json = [{'mac': c[0], 'ipv4': c[1], 'seen': utils.seconds_ago(c[2]), 'hostname': c[3]} for c in
                        clients]
        logger.debug('Returned {} clients to caller.'.format(len(clients_json)))
        return clients_json

    def truncate(self):
        if self._db_closed('truncate'):
            self.open()
        self.connection.execute('DELETE FROM labspion')
        self.connection.execute('DELETE FROM SQLITE_SEQUENCE WHERE name="labspion"')
        self.connection.commit()
        self.close()
        logger.debug('Truncated "{}".'.format(self.filename))
        self.open()


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


class DDWRT(Router):
    def __init__(self, conf, hostnames):
        self.hostnames = hostnames
        self.conf = conf
        self.auth = self.conf.auth()

    def clients(self):
        """ Receives all currently logged in users in a wifi network.

        :rtype : list
        :return: Returns a list of dicts, containing the following keys: mac, ipv4, seen, hostname
        """
        clients = self._get_clients_raw()

        clients_json = []
        for client in clients:
            client_ipv4 = client[0].strip()  # TODO: Insert actual IPv4 here
            client_mac = client[0].strip()
            client_hostname = self.hostnames.get(client_mac, u'Unbekannt').strip()

            clients_json.append({
                'mac': client_mac,
                'ipv4': client_ipv4,
                'seen': int(time.time()),
                'hostname': client_hostname,
            })

        logger.debug('The router got us {} clients.'.format(len(clients_json)))
        logger.debug(str(clients_json))
        return clients_json

    def _get_clients_raw(self):
        info_page = self.conf.internal()
        response = requests.get(info_page)
        while response.status_code != 200:
            logger.error("Could not retrieve {} (Code {}). Retrying...".format(info_page, response.status_code))
            response = requests.get(info_page)
        logger.info('Got response from router with code {}.'.format(response.status_code))
        return self._convert_to_clients(response.text) or []

    def _convert_to_clients(self, router_info_all):
        # Split router info in lines and filter empty info
        router_info_lines = filter(None, router_info_all.split("\n"))

        # Get key / value of router info
        router_info_items = {x[1:-1].split("::") for x in router_info_lines}

        # Get client info as a list
        client_info = router_info_items['active_wireless'].replace("'", "").split(",")

        # Group the list by each individual client
        # [['8C:70:5A:7A:2F:50', 'ath0', '0:20:45', '65M', '115M', '-50', '-92', '42', '540'], ...]
        clients = utils.groupn(client_info, 9)

        return clients if (len(clients) > 0) else []
