#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import os

__author__ = u'Jonas Gröger <jonas.groeger@gmail.com>'

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_FILE = os.path.join(PROJECT_PATH, 'database', 'labspion.db')
CONFIGURATION_FILE = os.path.join(PROJECT_PATH, 'labspion.ini')
