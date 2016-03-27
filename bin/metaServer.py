#!/usr/bin/env python

# LSST Data Management System
# Copyright 2015 AURA/LSST.
#
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the LSST License Statement and
# the GNU General Public License along with this program.  If not,
# see <http://www.lsstcorp.org/LegalNotices/>.

"""
This is a program for running RESTful LSST Metadata Server (only).
Use it for tests. It is really meant to run as part of the central
Web Service, e.g., through webserv/bin/server.py

@author  Jacek Becla, SLAC
"""

from flask import Flask, request
import json
import logging as log
import os
import sys

import ConfigParser
import sqlalchemy
from sqlalchemy.engine.url import URL

from lsst.dax.metaserv import metaREST_v0

app = Flask(__name__)


def initEngine():
    config = ConfigParser.ConfigParser()
    defaults_file = os.path.expanduser("~/.lsst/dbAuth-dbServ.ini")
    config.readfp(open(defaults_file))
    db_config = dict(config.items("mysql"))
    # Translate user name
    db_config["username"] = db_config["user"]
    del db_config["user"]
    # SQLAlchemy part
    url = URL("mysql", **db_config)
    return sqlalchemy.create_engine(url)

engine = initEngine()

app.config["default_engine"] = engine


@app.route('/')
def getRoot():
    fmt = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    s = '''Test server for testing metadata. Try adding /meta to URI.
'''
    if fmt == "text/html":
        return s
    return json.dumps(s)


@app.route('/meta')
def getMeta():
    '''Lists supported versions for /meta.'''
    fmt = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    s = '''v0
'''
    if fmt == "text/html":
        return s
    return json.dumps(s)

app.register_blueprint(metaREST_v0.metaREST, url_prefix='/meta/v0')

if __name__ == '__main__':
    log.basicConfig(
        format='%(asctime)s %(name)s %(levelname)s: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S',
        level=log.DEBUG)

    try:
        app.run(debug=True)
    except Exception, e:
        print "Problem starting the server.", str(e)
        sys.exit(1)
