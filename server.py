#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import os
import json

from flask.templating import render_template
from flask import Response

import database


__author__ = u'Jonas Gröger <jonas.groeger@gmail.com>'

from flask import Flask, redirect, url_for

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)
app.config.update(dict(
    DATABASE=os.path.join(PROJECT_DIR, 'labspion.db'),
    DEBUG=True,
    SECRET_KEY='JAS)Dha9sdh9asDHASd',
    USERNAME='nimda',
    PASSWORD='super-gut-yeah-21'
))
db = database.Database(app.config['DATABASE'])


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
    return render_template('index.html',
                           all_clients=c,
                           active_clients=c)


@app.route('/ueber')
def ueber():
    return render_template('ueber.html', author=__author__)


def main():
    app.run()


if __name__ == '__main__':
    main()
