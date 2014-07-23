#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import os
import pprint
import time
import ConfigParser
import logging
import re

import requests

__author__ = 'Jonas Gröger <jonas.groeger@gmail.com>'

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
INI_FILE = 'labspion.ini'

logging.basicConfig()
logging.getLogger(__name__).setLevel(logging.DEBUG)

hostname_table = {
    '00:87:40:8F:77:C6': u'Jonas Gröger Raspberry Pi',
    '8C:70:5A:7A:2F:50': u'Jonas Gröger Laptop',
    '10:68:3F:FA:4D:2D': u'Jonas Gröger Handy',
    'BC:F5:AC:F8:D2:0C': u'Sebastian Hof Handy',
    '54:26:96:CD:C0:6F': u'Sebastian Hof Laptop',
}


def _get_clients(website, username, password):
    response = requests.get(website, auth=(username, password))

    # Retry once on 401
    if response.status_code == 401:
        response = requests.get(website, auth=(username, password))

    if response.status_code != 200:
        raise IOError('Could not retrieve {} (Code {}).'.format(website, response.status_code))

    html = response.text
    first_script = html.partition('<script>')[2].partition('</script>')[0]
    mo = re.search('var attach_device_list="(.*)";', first_script)

    clients_js_var = mo.group(1)
    no_clients = not bool(clients_js_var.strip())
    return [] if no_clients else clients_js_var.split(' @\\#$\\&*! ')


def _read_login(config):
    section = 'labspion'
    website = config.get(section, 'website')
    username = config.get(section, 'username')
    password = config.get(section, 'password')

    return website, username, password


def _read_config(ini_file):
    config = ConfigParser.ConfigParser()
    if not config.read(ini_file):
        raise IOError('Could not find configuration file "{}".'.format(ini_file))

    return config


def _hostname_from_table(mac):
    return hostname_table.get(mac, None)


def active_clients():
    config = _read_config(os.path.join(PROJECT_DIR, INI_FILE))
    website, username, password = _read_login(config)
    clients = _get_clients(website, username, password)

    clients_json = []
    for client_as_string in clients:
        client = client_as_string.split(' ')
        client_ipv4 = client[0].strip()
        client_mac = client[1].strip()

        hostname_string = client[2].strip()
        hostname_from_router = None if hostname_string == '&lt;unknown&gt;' else hostname_string
        client_hostname = _hostname_from_table(client_mac) or hostname_from_router or u'Unbekannt'

        clients_json.append({
            'mac': client_mac,
            'ipv4': client_ipv4,
            'seen': int(time.time()),
            'hostname': client_hostname,
        })

    return clients_json


def main():
    clients_json = active_clients()
    pprint.pprint(clients_json)


if __name__ == '__main__':
    main()
