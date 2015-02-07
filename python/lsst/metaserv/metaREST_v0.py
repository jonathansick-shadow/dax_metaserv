#!/usr/bin/python

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
This module implements the RESTful interface for Metadata Service.
Corresponding URI: /meta

@author  Jacek Becla, SLAC
"""

from flask import Blueprint, Flask
import MySQLdb

metaREST = Blueprint('metaREST', __name__, template_folder='metaserv')

# connect to database metaServ
# todo: this will currently fail if metaServ db does not exist
# todo: db connection and credentials need to be handled better
dbHost = "localhost"
dbPort = 3306
dbUser="becla"
dbPass = ""
dbName = "metaServ"
con = MySQLdb.connect(host=dbHost, 
                      port=dbPort,
                      user=dbUser,
                      passwd=dbPass,
                      db=dbName)

# todo: known issue: it blocks commands such as "drop database", because
#       it keeps connection option. Close connection per request?


def runDbQuery1(query, notFoundMsg):
    '''Runs query that returns one row.'''
    cursor = con.cursor()
    cursor.execute(query)
    row = cursor.fetchone()
    if not row:
        retStr = notFoundMsg
    retStr = ''
    for x in range(0, len(row)):
        retStr += "%s: %s<br />" % (cursor.description[x][0], row[x])
    cursor.close()
    return retStr

def runDbQueryM(query, notFoundMsg):
    '''Runs query that returns many rows.'''
    cursor = con.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    if len(rows) == 0:
        retStr = notFoundMsg
    retStr = "<br />".join(str(r[0]) for r in rows)
    cursor.close()
    return retStr

@metaREST.route('/', methods=['GET'])
def getRoot():
    return '''
Hello, LSST Metadata Service here. Here is a list of types I support:<br />
  db<br />
  image<br />
'''

@metaREST.route('/db', methods=['GET'])
def getDb():
    '''Lists types of databases (that have at least one database).'''
    # todo: this will currently fail if Repo table does not exist
    return runDbQueryM(
        "SELECT DISTINCT lsstLevel FROM Repo WHERE repoType = 'db'",
        "No types with at least one database found.")

@metaREST.route('/db/<string:lsstLevel>', methods=['GET'])
def getDbPerType(lsstLevel):
    '''Lists databases for a given type.'''
    # todo: this will currently fail if Repo table does not exist
    return runDbQueryM(
        "SELECT dbName FROM Repo JOIN DbMeta on (repoId=dbMetaId) "
        "WHERE lsstLevel = '%s'" % lsstLevel,
        "No database found.")

@metaREST.route('/db/<string:lsstLevel>/<string:dbName>', methods=['GET'])
def getDbPerTypeDbName(lsstLevel, dbName):
    '''Retrieves information about one database.'''
    # We don't use lsstLevel here because db names are unique across all types.
    return runDbQuery1(
        "SELECT Repo.*, DbMeta.* "
        "FROM Repo JOIN DbMeta on (repoId=dbMetaId) "
        "WHERE dbName = '%s'" % dbName,
        "Database '%s' not found." % dbName)

@metaREST.route('/db/<string:lsstLevel>/<string:dbName>/tables', methods=['GET'])
def getDbPerTypeDbNameTables(lsstLevel, dbName):
    '''Lists table names in a given database.'''
    return runDbQueryM(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema='%s'" % dbName,
        "No tables found in database '%s'." % dbName)

@metaREST.route('/db/<string:lsstLevel>/<string:dbName>/tables/' +
                '<string:tableName>', methods=['GET'])
def getDbPerTypeDbNameTablesTableName(lsstLevel, dbName, tableName):
    '''Retrieves information about a table from a given database.'''
    return runDbQuery1(
        "SELECT DDT_Table.* FROM DDT_Table JOIN DbMeta USING (dbMetaId) "
        "WHERE dbName='%s' AND tableName='%s'" % (dbName, tableName),
        "Table '%s.%s'not found." % (dbName, tableName))

@metaREST.route('/db/<string:lsstLevel>/<string:dbName>/' +
                'tables/<string:tableName>/schema', methods=['GET'])
def getDbPerTypeDbNameTablesTableNameSchema(lsstLevel, dbName, tableName):
    '''Retrieves schema for a given table.'''
    return runDbQuery1(
        "SHOW CREATE TABLE %s.%s" % (dbName, tableName),
        "Table '%s.%s'not found." % (dbName, tableName))

@metaREST.route('/image', methods=['GET'])
def getImage():
    return ("meta/.../image not implemented. I am supposed to print list of " 
            "supported image types here, something like: raw, template, coadd, "
            "jpeg, calexp, ... etc")
