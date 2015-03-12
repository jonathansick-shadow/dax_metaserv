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
from optparse import OptionParser
import pprint
import re
import sys

from lsst.db.db import Db
from lsst.db.utils import readCredentialFile
from lsst.metaserv.schemaToMeta import SchemaToMeta
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
        x = SchemaToMeta(schemaFile)
        theTable = x.parse()

        # Fetch the schema information from the database
        ret = db.execCommandN(
            "SELECT table_name, column_name, ordinal_position "
            "FROM information_schema.COLUMNS WHERE "
            "TABLE_SCHEMA = %s ORDER BY table_name", (dbName,))

        # Count the number of columns in the ascii file
        nColumns = 0

        for t in theTable:
            nColumns += len(theTable[t]["columns"])

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
                    msg = "Column '%s.%s' not found in " % (tName, cName)
                    msg += "ascii file, present in db."
                    self._log.error(msg)
                    raise MetaBException(MetaBException.COL_NOT_IN_FL, cName, tName)

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

        # This can be sometimes handy for debugging
        # pp = pprint.PrettyPrinter(indent=2)
        # pp.pprint(theTable)

        # Get host/port from authFile
        dict = readCredentialFile(dbMysqlAuthF, self._log)
        (host, port) = [dict[k] for k in ('host', 'port')]

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
        cmd += "version, shortName, description, ownerId) "
        cmd += "VALUES('/dummy',%s,'db',%s,%s,%s,%s,%s,%s) "
        opts = (str(projectId), level, dataRel, schemaVersion, dbName, schemaDescr,
                str(ownerId))
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
        cmd = "INSERT INTO Institution(instName) VALUES(%s)"
        db.execCommand0(cmd, (name,))

    def addProject(self, name):
        """
        Add project.

        @param name  the name
        """
        db = Db(read_default_file=self._msMysqlAuthF)
        cmd = "INSERT INTO Project(projectName) VALUES(%s)"
        db.execCommand0(cmd, (name,))

####################################################################################
####################################################################################
####################################################################################
class CommandParser(object):
    """
    Parse commands and calls appropriate function from MetaAdminImpl
    """

    def __init__(self, msAuthFileName):
        """
        Initialize shared metadata, including list of supported commands.

        @param msAuthFileName file name of the file containing metaserv
                              mysql authorization.
        """
        self._msAuthFileName = msAuthFileName
        self._funcMap = {
            'ADD':        self._parseAdd,
            'EXIT':       self._justExit,
            'HELP':       self._printHelp,
            'QUIT':       self._justExit
            }
        self._impl = MetaAdminImpl(msAuthFileName)
        self._supportedCommands = """
  Supported commands:

    ADD DBDESCR <dbName> <schemaFile> <level> <dataRel> <owner> <accessibility>
                <project> <mysqlAuthFile>;

    It adds a database along with additional schema description provided through
    <schemaFile>. Parameters:
     <dbName>
         Database name. The database must exist, and should contain the
         schema that we are loading into metaserv.

     <schemaFile>
         Ascii file containing additional description of the schema. The
         description can include description of tables, columns, as well as
         special tokens, such as units or ucds.

     <level>
         Supported values are: DC, L1, L2, L3, dev.

     <dataRel>
         Data release (a string)

     <owner>
         mysqlUserName of the owner. The user should be known (it should be in the
         User table).

     <Accessibility>
         Supported values are: released, unreleased, private"

     <project>
         Name of the project associated with this database. It defaults to 'LSST'.

     <mysqlAuthFile>
         Connection parameters. It defaults to the value specified via -a option.
         Use it if the database is on a different server than metaserv.

    --------------------------------------------------------------------------------

    ADD DB <dbName> <level> <dataRel> <owner> <accessibility> <project>
           <mysqlAuthFile>;

    It adds a database without any additional schema description. All the rest is
    the same as for ADD DBDESCR.

    Note: this is not implemented. See DM-2301

    --------------------------------------------------------------------------------

    ADD INSTITUTION <name>;

    --------------------------------------------------------------------------------

    ADD PROJECT <name>;

    --------------------------------------------------------------------------------

    ADD USER <mysqlUserName> <firstName> <lastName> <affilliation> <email>;

    Adds a user. In the future this will create mysql user account
    (e.g., on lsst10). <Affilliation> should be set to an existing <instShortName>
    (these can be added using "ADD INSTITUTION" command.)

    --------------------------------------------------------------------------------

    QUIT;

    --------------------------------------------------------------------------------

    EXIT;

    --------------------------------------------------------------------------------

    ...more coming soon

"""

    def receiveCommands(self):
        """
        Receive user commands. End of command is determined by ';'. Multiple
        commands per line are allowed. Multi-line commands are allowed. To
        terminate: CTRL-D, or 'exit;' or 'quit;'.
        """
        line = ''
        cmd = ''
        prompt = "metab > "
        while True:
            line = raw_input(prompt).decode("utf-8").strip()
            cmd += line + ' '
            prompt = "metab > " if line.endswith(';') else "~ "
            while re.search(';', cmd):
                pos = cmd.index(';')
                try:
                    self._parse(cmd[:pos])
                except (MetaBException) as e:
                    log.error(e.__str__())
                    print "ERROR: ", e.__str__()
                cmd = cmd[pos+1:]

    def _parse(self, cmd):
        """
        Parse, and dispatch to subparsers based on first word. Raise exceptions on
        errors.
        """
        cmd = cmd.strip()
        # ignore empty commands, these can be generated by typing ;;
        if len(cmd) == 0: return
        tokens = cmd.split()
        tokens = [t.encode('utf8') for t in tokens]
        t = tokens[0].upper()
        if t in self._funcMap:
            self._funcMap[t](tokens[1:])
        else:
            raise MetaBException(MetaBException.NOT_IMPLEMENTED, cmd)

    def _parseAdd(self, tokens):
        """
        Subparser - handles ADD requests.
        """
        t = tokens[0].upper()
        if t == 'DBDESCR':
            self._parseAddDbDescr(tokens[1:])
        elif t == 'INSTITUTION':
            self._parseAddInstitution(tokens[1:])
        elif t == 'PROJECT':
            self._parseAddProject(tokens[1:])
        elif t == 'USER':
            self._parseAddUser(tokens[1:])
        else:
            raise MetaBException(MetaBException.BAD_CMD)

    def _parseAddDbDescr(self, tokens):
        l = len(tokens)
        if l < 6 or l > 8:
            raise MetaBException(MetaBException.BAD_CMD,
                                 "Unexpected number of arguments.")

        (dbName, schemaFile, level, dataRel, owner, accessibility) = tokens[0:6]
        project = (tokens[6] if l > 6 else "LSST")
        dbMysqlAuthF = (tokens[7] if l > 7 else self._msAuthFileName)
        self._impl.addDbDescr(dbName, schemaFile, level, dataRel, owner,
                              accessibility, project, dbMysqlAuthF)

    def _parseAddInstitution(self, tokens):
        l = len(tokens)
        if l == 1:
            # tokens[0] = name
             self._impl.addInstitution(tokens[0])
        else:
             raise MetaBException(MetaBException.BAD_CMD,
                                  "Unexpected number of arguments.")

    def _parseAddProject(self, tokens):
        l = len(tokens)
        if l == 1:
            # tokens[0] = name
             self._impl.addProject(tokens[0])
        else:
             raise MetaBException(MetaBException.BAD_CMD,
                                  "Unexpected number of arguments.")

    def _parseAddUser(self, tokens):
        l = len(tokens)
        if l == 5:
            # tokens[0:5] = muName, fName, lName, affil, email
             self._impl.addUser(*tokens[0:5])
        else:
             raise MetaBException(MetaBException.BAD_CMD,
                                  "Unexpected number of arguments.")

    def _justExit(self, tokens):
        raise SystemExit()

    def _printHelp(self, tokens):
        """
        Print available commands.
        """
        print self._supportedCommands

####################################################################################

def getOptions():
    usage = \
"""

NAME
        metaAdmin - the admin program for managing MetaServ backend

SYNOPSIS
        metaAdmin [OPTIONS]

OPTIONS
   -v
        Verbosity threshold. Logging messages which are less severe than
        provided will be ignored. Expected value range: 0=50: (CRITICAL=50,
        ERROR=40, WARNING=30, INFO=20, DEBUG=10). Default value is ERROR.
   -f
        Name of the output log file. If not specified, the output goes to stderr.
   -a
        MySQL Authorization file with connection information to metaserv and
        credentials for metaserv. It defaults to ~/.lsst/dbAuth-metaServ.txt.
"""

    parser = OptionParser(usage=usage)
    parser.add_option("-v", dest="verbT", default=10) # default is DEBUG
    parser.add_option("-f", dest="logF", default=None)
    parser.add_option("-a", dest="authF", default='~/.lsst/dbAuth-metaServ.txt')
    (options, args) = parser.parse_args()
    if int(options.verbT) > 50: options.verbT = 50
    if int(options.verbT) <  0: options.verbT = 0
    return (int(options.verbT), options.logF, options.authF)

####################################################################################
if __name__ == '__main__':
    (verbosity, logFileName, msAuthFileName) = getOptions()

    # configure logging
    if logFileName:
        log.basicConfig(
            filename=logFileName,
            format='%(asctime)s %(name)s %(levelname)s: %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S',
            level=verbosity)
    else:
        log.basicConfig(
            format='%(asctime)s %(name)s %(levelname)s: %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S',
            level=verbosity)

    # wait for commands and process
    try:
        CommandParser(msAuthFileName).receiveCommands()
    except(KeyboardInterrupt, SystemExit, EOFError):
        print ""
