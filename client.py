#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import ConfigParser
import logging
import re
import sqlite3
import time

import requests

import utils


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
        clients = self.cursor.execute('SELECT l.mac, l.ipv4, l.seen, l.hostname FROM labspion AS l')
        clients_json = [{'mac': c[0], 'ipv4': c[1], 'seen': utils.seconds_ago(c[2]), 'hostname': c[3]} for c in
                        clients]
        self.close()
        return clients_json

    def truncate(self):
        if self._db_closed('truncate'):
            self.open()
        self.connection.execute('DELETE FROM labspion')
        self.connection.execute('DELETE FROM SQLITE_SEQUENCE WHERE name="labspion"')
        self.connection.commit()
        self.close()


class Router(object):
    def __init__(self, urls, auth):
        self.urls = urls
        self.auth = auth
        self.hostnames = None
        self.client_separator = ' @\\#$\\&*! '
        self.clients_js_var_regex = 'var attach_device_list="(.*)";'

    def _init_hostnames(self):
        self.hostnames = {
            '00:87:40:8F:77:C6': u'Jonas Gröger Raspberry Pi',
            '8C:70:5A:7A:2F:50': u'Jonas Gröger Laptop',
            '10:68:3F:FA:4D:2D': u'Jonas Gröger Handy',
            'BC:F5:AC:F8:D2:0C': u'Sebastian Hof Handy',
            '54:26:96:CD:C0:6F': u'Sebastian Hof Laptop',
        }

    def send_login(self):
        requests.get(self.urls['login'], auth=self.auth)

    def clients(self):
        clients = self._get_clients()

        clients_json = []
        for client_as_string in clients:
            client = client_as_string.split(' ')
            client_ipv4 = client[0].strip()
            client_mac = client[1].strip()

            hostname_string = client[2].strip()
            hostname_from_router = hostname_string if hostname_string != '&lt;unknown&gt;' else None

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

        # Retry once on 401
        if response.status_code == 401:
            response = requests.get(self.urls['devices'], auth=self.auth)

        if response.status_code != 200:
            raise IOError('Could not retrieve {} (Code {}).'.format(self.urls['devices'], response.status_code))

        return self._clients_from_html(response.text) or []

    def _clients_from_html(self, html):
        first_script = html.partition('<script>')[2].partition('</script>')[0]
        clients_js_var = re.search(self.clients_js_var_regex, first_script).group(1)
        no_clients = not bool(clients_js_var.strip())
        return None if no_clients else clients_js_var.split(self.client_separator)


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
        url = self.config.get(self.section, 'ip')  # TODO: Rename in ini to url
        page_login = self.config.get(self.section, 'login')  # TODO: Rename in ini to page_login
        return url + page_login

    def devices_url(self):
        url = self.config.get(self.section, 'ip')  # TODO: Rename in ini to url
        page_devices = self.config.get(self.section, 'page_devices')  # TODO: Rename in ini to page_devices
        return url + page_devices


    def username(self):
        return self.config.get(self.section, 'username')

    def password(self):
        return self.config.get(self.section, 'password')

    def auth(self):
        return self.username(), self.password()
