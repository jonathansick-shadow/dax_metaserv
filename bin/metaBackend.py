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
This is a program for ingesting information into LSST Metadata Server. 

@author  Jacek Becla, SLAC
"""

from lsst.db.db import Db, DbException
from lsst.db.utils import readCredentialFile
import lsst.log as log
import sys

creds = readCredentialFile("~/.lsst/dbAuth-metaServ.txt", log)

db = Db(user=creds["user"],
        host=creds["host"],
        port=int(creds["port"]),
        passwd=creds["passwd"],
        db=creds["db"])

def registerDb(dbName, level, projectName='LSST'):
    if not db.dbExists(dbName):
        log.error("Db not found")
        return
    cmd = "INSERT INTO Repo(url, project, repoType, lsstLevel, shortName, owner) "
    cmd += "VALUES('/dummy', '%s', 'db', '%s', '%s', 0) " % \
        (projectName, level, dbName)
    db.execCommand0(cmd)
    theId = db.execCommand1("SELECT LAST_INSERT_ID()")[0]
    cmd = "INSERT INTO DbMeta(dbMetaId, dbName) "
    cmd += "VALUES(%s, '%s')" % (theId, dbName)
    db.execCommand0(cmd)

    tables = db.listTables(dbName)     
    for t in tables:
        cmd = "INSERT INTO DDT_Table(dbMetaId, tableName) "
        cmd += "VALUES(%s, '%s')" % (theId, t)
        db.execCommand0(cmd)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print "Expecting 3 args"
        exit(-1)
    theCmd = sys.argv[1]
    dbName = sys.argv[2]
    level = sys.argv[3]
    if theCmd == 'regDb':
        print "cmd=%s, db=%s, l=%s" % (theCmd, dbName, level)
        registerDb(dbName, level)
    else:
        print 'Unsupported command. I support: regDb, [more coming soon]'
        exit(-2)
