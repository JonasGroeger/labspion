#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import json

from flask.templating import render_template
import time

from wifi_clients import active_clients, split_clients


__author__ = 'Jonas Gröger <jonas.groeger@gmail.com>'

from flask import Flask, redirect, url_for

app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
    return redirect(url_for('clients'))


@app.route('/clients')
def clients():
    all_clients = active_clients()
    # clients_now, clients_today = split_clients(all_clients, now=time.time())
    return render_template(all_clients)


@app.route('/clients/json')
def clients_json():
    # Header check application/json, header send application/json
    all_clients = active_clients()
    return json.dumps(all_clients)


def main():
    app.run()


if __name__ == '__main__':
    main()
