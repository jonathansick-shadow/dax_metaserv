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
LSST Metadata Server. It relies on MetaAdmin_Impl to do the actual work. The code
here is primarily responsible for parsing arguments.

@author  Jacek Becla, SLAC
"""

import logging as log
from optparse import OptionParser
import sys

from lsst.dax.metaserv.metaAdminImpl import MetaAdminImpl
from lsst.dax.metaserv.metaBException import MetaBException


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
            'ADD': self._parseAdd,
            'EXIT': self._justExit,
            'HELP': self._printHelp,
            'QUIT': self._justExit
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
            while ';' in cmd:
                pos = cmd.index(';')
                try:
                    self._parse(cmd[:pos])
                except (MetaBException) as e:
                    log.error("%s", e)
                cmd = cmd[pos+1:]

    def _parse(self, cmd):
        """
        Parse, and dispatch to subparsers based on first word. Raise exceptions on
        errors.
        """
        cmd = cmd.strip()
        # ignore empty commands, these can be generated by typing ;;
        if len(cmd) == 0:
            return
        tokens = cmd.split()
        tokens = [t for t in tokens]
        t = tokens[0].upper()
        if t in self._funcMap:
            self._funcMap[t](tokens[1:])
        else:
            raise MetaBException(MetaBException.NOT_IMPLEMENTED, cmd)

    def _parseAdd(self, tokens):
        """
        Subparser - handles ADD requests.
        """
        if not tokens:
            raise MetaBException(MetaBException.BAD_CMD, "Missing tokens for ADD")
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
        length = len(tokens)
        if length < 6 or length > 8:
            raise MetaBException(MetaBException.BAD_CMD,
                                 "Unexpected number of arguments.")

        (dbName, schemaFile, level, dataRel, owner, accessibility) = tokens[0:6]
        project = (tokens[6] if length > 6 else "LSST")
        dbMysqlAuthF = (tokens[7] if length > 7 else self._msAuthFileName)
        self._impl.addDbDescr(dbName, schemaFile, level, dataRel, owner,
                              accessibility, project, dbMysqlAuthF)

    def _parseAddInstitution(self, tokens):
        length = len(tokens)
        if length == 1:
            # tokens[0] = name
            self._impl.addInstitution(tokens[0])
        else:
            raise MetaBException(MetaBException.BAD_CMD,
                                 "Unexpected number of arguments.")

    def _parseAddProject(self, tokens):
        length = len(tokens)
        if length == 1:
            # tokens[0] = name
            self._impl.addProject(tokens[0])
        else:
            raise MetaBException(MetaBException.BAD_CMD,
                                 "Unexpected number of arguments.")

    def _parseAddUser(self, tokens):
        length = len(tokens)
        if length == 5:
            # tokens[0:5] = muName, fName, lName, affil, email
            self._impl.addUser(*tokens[0:5])
        else:
            raise MetaBException(MetaBException.BAD_CMD,
                                 "Unexpected number of arguments.")

    def _justExit(self, tokens):
        raise sys.exit()

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
        SQLAlchemy configuration file with connection information to metaserv and
        credentials for metaserv. It defaults to ~/.lsst/dbAuth-metaServ.ini.
"""

    parser = OptionParser(usage=usage)
    parser.add_option("-v", dest="verbT", default=10)  # default is DEBUG
    parser.add_option("-f", dest="logF", default=None)
    parser.add_option("-a", dest="authF", default='~/.lsst/dbAuth-metaServ.ini')
    (options, args) = parser.parse_args()
    if int(options.verbT) > 50:
        options.verbT = 50
    if int(options.verbT) < 0:
        options.verbT = 0
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
