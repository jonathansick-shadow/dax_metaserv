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
Metadata Server admin program. It is currently used to ingest information into the
LSST Metadata Server.

@author  Jacek Becla, SLAC
"""

import logging as log
# import pprint
import re

from lsst.db.db import Db
from lsst.db.utils import readCredentialFile
from lsst.metaserv.schemaToMeta import parseSchema
from lsst.metaserv.metaBException import MetaBException


class MetaAdminImpl(object):
    """
    Implements the guts of the metaserver admin program."
    """

    def __init__(self, msMysqlAuthF):
        """
        @param msMysqlAuthF  mysql auth file for metaserv db and metaserv user
        """
        self._msMysqlAuthF = msMysqlAuthF
        self._log = log.getLogger("lsst.metaserv.admin")

    def addDbDescr(self, dbName, schemaFile, level, dataRel, owner,
                   accessibility, projectName, dbMysqlAuthF):
        """
        Add a database along with additional schema description provided through
        @schemaFile.

        @param dbName        database name
        @param schemaFile    ascii file containing schema with description
        @param level         level (e.g., L1, L2, L3)
        @param dataRel       data release
        @param owner         owner of the database
        @param accessibility accessibility of the database (pending/public/private)
        @param projectName   name of the project the db is associated with
        @param dbMysqlAuthF  mysql auth file for the db that we are adding

        The function connects to two database servers:
        a) one that has the database that is being loaded
        b) one that has the metaserv database
        If they are both on the same server, the connection is reused.

        The course of action:
        * connect to the server that has database that is being loaded
        * parse the ascii schema file
        * fetch schema information from the information_schema
        * do the matching, add info fetched from information_schema to the
          in memory structure produced by parsing ascii schema file
        * fetch schema description and version (which is kept as data inside
          a special table in the database that is being loaded). Ignore if it
          does not exist.
        * Capture information from mysql auth file about connection information
        * connect to the metaserv database
        * validate owner, project (these must be loaded into metaserv prior to
        calling this function)
        * load all the information into metaserv in various tables (Repo,
          DDT_Table, DDT_Column)

        It raises following MetaBEXceptions:
        * DB_DOES_NOT_EXISTS if database dbName does not exist
        * NOT_MATCHING if the database schema and ascii schema don't match
        * TB_NOT_IN_DB if the table is described in ascii schema, but it is missing
                       in the database
        * COL_NOT_IN_TB if the column is described in ascii schema, but it is
                        missing in the database
        * COL_NOT_IN_FL if the column is in the database schema, but not in ascii
                        schema
        * Db object can throw various DbException and MySQL exceptions
        """

        # Connect to the server that has database that is being added
        db = Db(read_default_file=dbMysqlAuthF)
        if not db.dbExists(dbName):
            self._log.error("Db '%s' not found.", dbName)
            raise MetaBException(MetaBException.DB_DOES_NOT_EXIST, dbName)

        # Parse the ascii schema file
        theTable = parseSchema(schemaFile)

        # Fetch the schema information from the database
        ret = db.execCommandN(
            "SELECT table_name, column_name, ordinal_position "
            "FROM information_schema.COLUMNS WHERE "
            "TABLE_SCHEMA = %s ORDER BY table_name", (dbName,))

        # Count the number of columns in the ascii file
        nColumns = sum(len(t["columns"]) for t in theTable.values())

        # Check if the number of columns matches
        if nColumns != len(ret):
            self._log.error("Number of columns in ascii file "
                       "(%d) != number of columns in db (%d)", nColumns, len(ret))
            raise MetaBException(MetaBException.NOT_MATCHING)

        # Fetch ordinal_positions from information_schema and add it to "theTable"
        for (tName, cName, ordP) in ret:
            t = theTable.get(tName, None)
            if not t:
                self._log.error(
                    "Table '%s' not found in db, present in ascii file.", tName)
                raise MetaBException(MetaBException.TB_NOT_IN_DB, tName)
            foundColumn = False
            for c in t["columns"]:
                if c["name"] == cName:
                    foundColumn = True
                    c["ord_pos"] = int(ordP)
                    break
        if not foundColumn:
            self._log.error(
                "Column '%s.%s' not found in db, present in ascii file.",
                tName, cName)
            raise MetaBException(MetaBException.COL_NOT_IN_TB, cName, tName)

        # Check if we covered all columns
        for t in theTable:
            for c in theTable[t]["columns"]:
                if "ord_pos" not in c:
                    self._log.error(
                        "Column '%s.%s' not found in ascii file, present in db.",
                        t, c)
                    raise MetaBException(MetaBException.COL_NOT_IN_FL, str(c), str(t))

        # Get schema description and version, it is ok if it is missing
        ret = db.execCommand1(
            "SELECT version, descr FROM %s.ZZZ_Schema_Description" % dbName)
        if not ret:
            self._log.error(
                "Db '%s' does not contain schema version/description", dbName)
            schemaVersion = "unknown"
            schemaDescr = ""
        else:
            (schemaVersion, schemaDescr) = ret

        # This can be sometimes handy for debugging. (uncomment import too)
        # pp = pprint.PrettyPrinter(indent=2)
        # pp.pprint(theTable)

        # Get host/port from authFile
        hpDict = readCredentialFile(dbMysqlAuthF, self._log)
        (host, port) = [hpDict[k] for k in ('host', 'port')]

        # Now, we will be talking to the metaserv database, so change
        # connection as needed
        if self._msMysqlAuthF != dbMysqlAuthF:
            db = Db(read_default_file=self._msMysqlAuthF)

        # get ownerId, this serves as validation that this is a valid owner name
        ret = db.execCommand1("SELECT userId FROM User WHERE mysqlUserName = %s",
                              (owner,))
        if not ret:
            self._log.error("Owner '%s' not found.", owner)
            raise MetaBException(MetaBException.OWNER_NOT_FOUND, owner)
        ownerId = ret[0]

        # get projectId, this serves as validation that this is a valid project name
        ret = db.execCommand1("SELECT projectId FROM Project WHERE projectName =%s",
                              (projectName,))
        if not ret:
            self._log.error("Project '%s' not found.", owner)
            raise MetaBException(MetaBException.PROJECT_NOT_FOUND, projectName)
        projectId = ret[0]

        # Finally, save things in the MetaServ database
        cmd = "INSERT INTO Repo(url, projectId, repoType, lsstLevel, dataRelease, "
        cmd += "version, shortName, description, ownerId, accessibility) "
        cmd += "VALUES('/dummy',%s,'db',%s,%s,%s,%s,%s,%s,%s) "
        opts = (str(projectId), level, dataRel, schemaVersion, dbName, schemaDescr,
                str(ownerId), accessibility)
        db.execCommand0(cmd, opts)
        repoId = db.execCommand1("SELECT LAST_INSERT_ID()")[0]
        cmd = "INSERT INTO DbMeta(dbMetaId, dbName, connHost, connPort) "
        cmd += "VALUES(%s,%s,%s,%s)"
        db.execCommand0(cmd, (str(repoId), dbName, host, str(port)))

        for t in theTable:
            cmd = 'INSERT INTO DDT_Table(dbMetaId, tableName, descr) '
            cmd += 'VALUES(%s, %s, %s)'
            db.execCommand0(cmd, (str(repoId), t,
                                  theTable[t].get("description", "")))
            tableId = db.execCommand1("SELECT LAST_INSERT_ID()")[0]
            isFirst = True
            for c in theTable[t]["columns"]:
                if isFirst:
                    cmd = 'INSERT INTO DDT_Column(columnName, tableId, '
                    cmd += 'ordinalPosition, descr, ucd, units) VALUES '
                    opts = ()
                    isFirst = False
                else:
                    cmd += ', '
                cmd += '(%s, %s, %s, %s, %s, %s)'
                opts += (c["name"], str(tableId), str(c["ord_pos"]),
                         c.get("description", ""), c.get("ucd", ""),
                         c.get("unit", ""))
            db.execCommand0(cmd, opts)

    def addUser(self, muName, fName, lName, affil, email):
        """
        Add user.

        @param muName MySQL user name
        @param fName  first name
        @param lName  last name
        @param affil  short name of the affilliation (home institution)
        @param email  email address
        """
        db = Db(read_default_file=self._msMysqlAuthF)
        cmd = "SELECT instId FROM Institution WHERE instName = %s"
        instId = db.execCommand1(cmd, (affil,))
        if instId is None:
            raise MetaBException(MetaBException.INST_NOT_FOUND, affil)
        cmd = "INSERT INTO User(mysqlUserName, firstName, lastName, email, instId) "
        cmd += "VALUES(%s, %s, %s, %s, %s)"
        db.execCommand0(cmd, (muName, fName, lName, email, str(instId[0])))

    def addInstitution(self, name):
        """
        Add institution.

        @param name  the name
        """
        db = Db(read_default_file=self._msMysqlAuthF)
        ret = db.execCommand1(
            "SELECT COUNT(*) FROM Institution WHERE instName=%s", (name,))
        if ret[0] == 1:
            raise MetaBException(MetaBException.INST_EXISTS, name)
        db.execCommand0("INSERT INTO Institution(instName) VALUES(%s)", (name,))

    def addProject(self, name):
        """
        Add project.

        @param name  the name
        """
        db = Db(read_default_file=self._msMysqlAuthF)
        ret = db.execCommand1(
            "SELECT COUNT(*) FROM Project WHERE projectName=%s", (name,))
        if ret[0] == 1:
            raise MetaBException(MetaBException.PROJECT_EXISTS, name)
        db.execCommand0("INSERT INTO Project(projectName) VALUES(%s)", (name,))
