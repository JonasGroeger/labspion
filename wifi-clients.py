#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from ConfigParser import NoSectionError, NoOptionError
import pprint
import subprocess
import shlex
import time
import ConfigParser
import logging

from lxml import etree


__author__ = 'Jonas Gröger <jonas.groeger@gmail.com>'

CONFIG_FILE = '.config.cfg'
DEVELOPMENT_MODE = True

logging.basicConfig()
logging.getLogger(__name__).setLevel(logging.DEBUG)


def _get_connected_clients(sudo_password):
    nmap_cmd = 'sudo nmap -sP 192.168.178.0/24 -oX -'

    p = subprocess.Popen(shlex.split(nmap_cmd), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.stdin.write(sudo_password + '\n')
    p.stdin.flush()
    out, err = p.communicate()

    return out


def _make_client_list(clients_xml):
    # Only clients with mac are relevant
    root = etree.fromstring(clients_xml)
    clients_with_mac = root.xpath('//host[address[@addrtype="mac"]]')

    clients_json = []
    for client_id, client in enumerate(clients_with_mac):

        try:
            client_mac = client.xpath('./address[@addrtype="mac"]/@addr')[0]
        except IndexError:
            logging.debug('No MAC for client {}.'.format(client_id))
            continue  # We identify clients by mac. So skip ones without mac

        try:
            client_ipv4 = client.xpath('./address[@addrtype="ipv4"]/@addr')[0]
        except IndexError:
            logging.debug('No IPv4 for client {} ({}).'.format(client_id, client_mac))
            client_ipv4 = None

        try:
            client_ipv6 = client.xpath('./address[@addrtype="ipv6"]/@addr')[0]
        except IndexError:
            logging.debug('No IPv6 for client {} ({}).'.format(client_id, client_mac))
            client_ipv6 = None

        try:
            client_hostname = client.xpath('./hostnames//hostname')[0].xpath('@name')[0]
        except IndexError:
            logging.debug('No hostname for client {} ({}).'.format(client_id, client_mac))
            client_hostname = None

        clients_json.append({
            'id': client_id,
            'mac': client_mac,
            'ipv4': client_ipv4,
            'ipv6': client_ipv6,
            'hostname': client_hostname,
            'seen': int(time.time()),
        })

    return clients_json


def _get_clients_xml(sudo_password=None):
    if DEVELOPMENT_MODE:
        logging.debug('Reading clients from local "clients.xml".')
        with open('clients.xml', 'r') as f:
            clients_xml = f.read()
    else:
        logging.debug('Reading clients from nmap.')
        clients_xml = _get_connected_clients(sudo_password)
        logging.warning('There were no connected clients.')

        with open('clients.xml', 'w') as f:
            f.write(clients_xml)

    return clients_xml


def _get_sudo_password():
    config = ConfigParser.ConfigParser()
    sudo_password = None
    try:
        config.read(CONFIG_FILE)
        sudo_password = config.get('labspion', 'sudo_password')
    except IOError:
        logging.error('Could not find the configuration file "{}". Please create one.'.format(CONFIG_FILE))
        exit(1)
    except (NoSectionError, NoOptionError):
        logging.error('The configuration file must contain a section "[labspion]" with a key "sudo_password"')
        exit(2)
    if sudo_password in [None, '']:
        logging.warning('The sudo password is empty. Really? I\'m using it anyway.')

    return sudo_password


def main():
    sudo_password = _get_sudo_password()

    clients_xml = _get_clients_xml(sudo_password)
    clients_json = _make_client_list(clients_xml)

    pprint.pprint(clients_json)


if __name__ == '__main__':
    main()
