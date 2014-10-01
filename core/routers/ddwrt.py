# -*- coding: utf-8 -*-
import logging
import time

import requests
from requests.structures import CaseInsensitiveDict

from core import utils
from core.client import Router


__author__ = u'Jonas Gröger <jonas.groeger@gmail.com>'

logger = logging.getLogger('labspion.routers')


class DDWRT(Router):
    def __init__(self, conf, hostnames):
        self.hostnames = CaseInsensitiveDict()
        self.hostnames.update(hostnames)
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
            client_hostname_from_router = client[0]
            client_ipv4 = client[1].strip()
            client_mac = client[2].strip().upper()
            client_hostname = self.hostnames.get(client_mac, client_hostname_from_router).strip()
            client_connections = int(client[3].strip())

            # Clients with less than 20 connections are considered offline
            if client_connections < 20:
                continue

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
        response = requests.get(info_page, auth=self.auth)
        logger.info('Got response from router with code {}.'.format(response.status_code))
        return DDWRT._convert_to_clients(response.text) or []

    @staticmethod
    def _convert_to_clients(router_info_all):
        # Split router info in lines and filter empty info
        router_info_lines = filter(None, router_info_all.split("\n"))

        # Get key / value of router info
        router_info_items = dict()
        for item in router_info_lines:
            key, value = item[1:-1].split("::")  # Remove curly braces and split
            router_info_items[key.strip()] = value.strip()

        # Get client info as a list
        arp_table = utils.groupn(router_info_items['arp_table'].replace("'", "").split(","), 4)
        dhcp_leases = utils.groupn(router_info_items['dhcp_leases'].replace("'", "").split(","), 5)

        return arp_table if (len(arp_table) > 0) else []
