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
from lsst.metaserv import metaREST_v0

app = Flask(__name__)

@app.route('/')
def getRoot():
    return '''Test server for testing metadata. Try adding /meta to URI.
'''

@app.route('/meta')
def getMeta():
    '''Lists supported versions for /meta.'''
    return '''v0
'''

app.register_blueprint(metaREST_v0.metaREST, url_prefix='/meta/v0')

if __name__ == '__main__':
    app.run(debug=True)
