#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import pprint
import time
import ConfigParser
import logging

import pyesprima
import requests
from requests.auth import HTTPBasicAuth


__author__ = 'Jonas Gröger <jonas.groeger@gmail.com>'

INI_FILE = 'labspion.ini'

logging.basicConfig()
logging.getLogger(__name__).setLevel(logging.DEBUG)


def _get_clients(website, username, password):
    response = requests.get(website, auth=HTTPBasicAuth(username, password))

    print response.status_code
    if response.status_code != 200:
        raise IOError('Could not retrieve {}'.format(website))

    html = response.text
    first_script = html.partition('<script>')[2].partition('</script>')[0]
    clients_as_string = pyesprima.parse(first_script).body[1].declarations[0].init.value

    return clients_as_string.split(' @#$&*! ')


def _read_login(config):
    section = 'labspion'
    website = config.get(section, 'website')
    username = config.get(section, 'username')
    password = config.get(section, 'password')

    return (website, username, password)


def _read_config(ini_file):
    config = ConfigParser.ConfigParser()
    if config.read(ini_file) == []:
        raise IOError('Could not find configuration file "{}".'.format(ini_file))

    return config


def _make_client_list():
    config = _read_config(INI_FILE)
    website, username, password = _read_login(config)
    clients = _get_clients(website, username, password)

    clients_json = []
    for client_id, client_as_string in enumerate(clients):
        client = client_as_string.split(' ')

        client_ip = client[0].strip()
        client_mac = client[1].strip()
        client_hostname = client[2].strip()

        clients_json.append({
            'id': client_id,
            'ipv4': client_ip,
            'mac': client_mac,
            'hostname': client_hostname,
            'seen': int(time.time()),
        })

    return clients_json


def main():
    clients_json = _make_client_list()
    pprint.pprint(clients_json)


if __name__ == '__main__':
    main()
