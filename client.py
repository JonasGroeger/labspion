#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import ConfigParser
import logging
import re
import sqlite3
import time

import requests

import trollius as asyncio

import utils
from utils import seconds_until_hour


__author__ = u'Jonas Gröger <jonas.groeger@gmail.com>'


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

    def login_url(self):
        url = self.config.get(self.section, 'url')
        page_login = self.config.get(self.section, 'page_login')
        return url + page_login

    def devices_url(self):
        url = self.config.get(self.section, 'url')
        page_devices = self.config.get(self.section, 'page_devices')
        return url + page_devices

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
            self.open()
        self.cursor.executemany('INSERT INTO labspion VALUES (NULL ,?,?,?,?)', clients_json)
        self.connection.commit()
        self.close()

    def clients(self):
        self.open()
        sql = 'SELECT l.mac, l.ipv4, max(l.seen) AS seen, l.hostname FROM labspion AS l GROUP BY l.mac'
        clients = self.cursor.execute(sql)
        clients_json = [{'mac': c[0], 'ipv4': c[1], 'seen': utils.seconds_ago(c[2]), 'hostname': c[3]} for c in
                        clients]
        self.close()
        return clients_json

    @asyncio.coroutine
    def truncate(self):
        while True:
            yield asyncio.From(asyncio.sleep(seconds_until_hour(4)))
            if self._db_closed('truncate'):
                self.open()
            self.connection.execute('DELETE FROM labspion')
            self.connection.execute('DELETE FROM SQLITE_SEQUENCE WHERE name="labspion"')
            self.connection.commit()
            self.close()
            self.open()


class Labspion(object):
    def __init__(self, database, router):
        self.database = database
        self.router = router

    @staticmethod
    def _database_tuple(clients_dict):
        return [(c['mac'], c['ipv4'], c['seen'], c['hostname']) for c in clients_dict]

    @asyncio.coroutine
    def run(self):
        while True:
            clients_dict = self.router.recv_clients()

            # We need to make sure the order is right
            clients_tuple = Labspion._database_tuple(clients_dict)

            self.database.insert(clients_tuple)
            yield asyncio.From(asyncio.sleep(10))


class Router(object):
    def __init__(self, urls, auth, hostnames=None):
        if not hostnames:
            self.hostnames = dict()
        else:
            self.hostnames = hostnames
        self.urls = urls
        self.auth = auth
        self._client_separator = ' @\\#$\\&*! '
        self._clients_js_var_regex = 'var attach_device_list="(.*)";'

    def send_login(self):
        requests.get(self.urls['login'], auth=self.auth)

    def recv_clients(self):
        """ Receives all currently logged in users in a wifi network.

        :rtype : list
        :return: Returns a list of dicts, containing the following keys: mac, ipv4, seen, hostname
        """
        clients = self._get_clients()

        clients_json = []
        for client_as_string in clients:
            client = client_as_string.split(' ')
            client_ipv4 = client[0].strip()
            client_mac = client[1].strip()

            # The hostname is is somestimes 'unknown'.
            hostname_string = client[2].strip()
            hostname_from_router = hostname_string if hostname_string != '&lt;unknown&gt;' else None

            # Hostname lookup order: Hostname table, Hostname from router, 'Unbekannt'
            client_hostname = self.hostnames[client_mac] or hostname_from_router or u'Unbekannt'

            clients_json.append({
                'mac': client_mac,
                'ipv4': client_ipv4,
                'seen': int(time.time()),
                'hostname': client_hostname,
            })

        return clients_json

    def _get_clients(self):
        response = requests.get(self.urls['devices'], auth=self.auth)
        while response.status_code != 200:
            logging.error('Could not retrieve {} (Code {}).'.format(self.urls['devices'], response.status_code))
            response = requests.get(self.urls['devices'], auth=self.auth)
        return self._clients_from_html(response.text) or []

    def _clients_from_html(self, html):
        first_script = html.partition('<script>')[2].partition('</script>')[0]
        clients_js_var = re.search(self._clients_js_var_regex, first_script).group(1)
        no_clients = not bool(clients_js_var.strip())
        return [] if no_clients else clients_js_var.split(self._client_separator)
