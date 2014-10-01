#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from core import client, DATABASE_FILE


__author__ = u'Jonas Gröger <jonas.groeger@gmail.com>'


def main():
    database = client.Database(DATABASE_FILE)
    database.truncate()
    database.close()


if __name__ == '__main__':
    main()
