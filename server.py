#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import json

from flask.templating import render_template
from flask import Response
from flask import Flask, redirect, url_for

from labspion import client
import labspion


__author__ = u'Jonas Gröger <jonas.groeger@gmail.com>'

app = Flask(__name__)
app.config.update({
    'DATABASE': labspion.DATABASE_FILE,
    'DEBUG': True
})
db = client.Database(app.config['DATABASE'])


@app.route('/')
def index():
    return redirect(url_for('clients'))


@app.route('/json')
def clients_json():
    c = db.clients()
    return Response(json.dumps({
        'all_clients': c,
        'active_clients': c,
    }), mimetype='application/json')


@app.route('/clients')
def clients():
    c = db.clients()
    return render_template('index.html', clients=c)


@app.route('/ueber')
def ueber():
    return render_template('ueber.html', author=__author__)


def main():
    app.run()


if __name__ == '__main__':
    main()
