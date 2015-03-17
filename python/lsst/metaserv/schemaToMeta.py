#!/usr/bin/env python
#
# LSST Data Management System
# Copyright 2008-2015 LSST Corporation.
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


import os
import pprint
import re
import sys

class SchemaToMeta(object):
    """
    SchemaToMeta class parses mysql schema file that can optionally contain
    extra tokens in comments. Extracts information for each table:
    * name
    * engine
    * per column:
      - type
      - notnull
      - defaultValue
      - <descr>...</descr>
      - <unit>...</unit>
      - <ucd>...</ucd>
    and saves it in an array.

    This code was originally written for schema browser
    (in cat/bin/schema_to_metadata.py).
    """

    _tableStart = re.compile(r'CREATE TABLE (\w+)*')
    _tableEnd = re.compile(r"\)")
    _engineLine = re.compile(r'\) (ENGINE|TYPE)=(\w+)*;')
    _columnLine = re.compile(r'[\s]+(\w+) ([\w\(\)]+)')
    _unitLine = re.compile(r'<unit>(.+)</unit>')
    _ucdLine = re.compile(r'<ucd>(.+)</ucd>')
    _descrLine = re.compile(r'<descr>(.+)</descr>')
    _descrStart = re.compile(r'<descr>(.+)')
    _descrMiddle = re.compile(r'\s*--(.+)')
    _descrEnd = re.compile(r'\s*--(.+)</descr>')

    def __init__(self, inputFileName):
        """
        Constructor, prepares for execution.

        @param inputFileName:   ASCII file containing the schem to be parsed
        """
        if not os.path.isfile(inputFileName):
            sys.stderr.write("File '%s' does not exist\n" % inputFileName)
            sys.exit(1)
        self._inFName = inputFileName

    def parse(self):
        """Do actual parsing. Returns the retrieved structure as a table. The
        structure of the produced table:
{ <tableName1>: {
    'columns': [ { 'description': <column description>,
                   'displayOrder': <value>,
                   'name': <value>,
                   'notNull': <value>,
                   'ord_pos': <value>,
                   'type': <type> },
                 # repeated for every column
               ]
    'description': <table description>,
    'engine': <engine>,
    'indexes': [ { 'columns': <column name>,
                   'type': <type>},
                 # repeated for every index
               ]
  }
  # repeated for every table
}
"""
        in_table = None
        in_col = None
        in_colDescr = None
        table = {}

        colNum = 1

        iF = open(self._inFName, mode='r')
        for line in iF:
            # print "processing ", line
            m = SchemaToMeta._tableStart.search(line)
            if m is not None:
                tableName = m.group(1)
                table[tableName] = {}
                colNum = 1
                in_table = table[tableName]
                in_col = None
                #print "Found table ", in_table
            elif SchemaToMeta._tableEnd.match(line):
                m = SchemaToMeta._engineLine.match(line)
                if m is not None:
                    engineName = m.group(2)
                    in_table["engine"] = engineName
                # print "end of the table"
                # print in_table
                in_table = None
            elif in_table is not None: # process columns for given table
                m = SchemaToMeta._columnLine.match(line)
                if m is not None:
                    firstWord = m.group(1)
                    if self._isIndexDefinition(firstWord):
                        t = "-"
                        if firstWord == "PRIMARY":
                            t = "PRIMARY KEY"
                        elif firstWord == "UNIQUE":
                            t = "UNIQUE"
                        idxInfo = {"type" : t,
                                   "columns" : self._retrColumns(line)
                               }
                        in_table.setdefault("indexes", []).append(idxInfo)
                    else:
                        in_col = {"name" : firstWord,
                                  "displayOrder" : str(colNum),
                                  "type" : self._retrType(line),
                                  "notNull" : self._retrIsNotNull(line),
                              }
                        dv = self._retrDefaultValue(line)
                        if dv is not None:
                            in_col["defaultValue"] = dv
                        colNum += 1
                        if "columns" not in in_table:
                            in_table["columns"] = []
                        in_table["columns"].append(in_col)
                    # print "found col: ", in_col
                elif self._isCommentLine(line): # handle comments
                    if in_col is None:    # table comment

                        if self._containsDescrTagStart(line):
                            if self._containsDescrTagEnd(line):
                                in_table["description"] = self._retrDescr(line)
                            else:
                                in_table["description"] = self._retrDescrStart(line)
                        elif "description" in in_table:
                            if self._containsDescrTagEnd(line):
                                in_table["description"] += self._retrDescrEnd(line)
                            else:
                                in_table["description"] += self._retrDescrMid(line)
                    else:
                                          # column comment
                        if self._containsDescrTagStart(line):
                            if self._containsDescrTagEnd(line):
                                in_col["description"] = self._retrDescr(line)
                            else:
                                in_col["description"] = self._retrDescrStart(line)
                                in_colDescr = 1
                        elif in_colDescr:
                            if self._containsDescrTagEnd(line):
                                in_col["description"] += self._retrDescrEnd(line)
                                in_colDescr = None
                            else:
                                in_col["description"] += self._retrDescrMid(line)

                                          # units
                        if self._isUnitLine(line):
                            in_col["unit"] = self._retrUnit(line)

                                          # ucds
                        if self._isUcdLine(line):
                            in_col["ucd"] = self._retrUcd(line)

        iF.close()
        return table

    ###########################################################################
    # Helper functions
    ###########################################################################

    def _isIndexDefinition(self, c):
        return c in ["PRIMARY", "KEY", "INDEX", "UNIQUE"]

    def _isCommentLine(self, str):
        return re.match(r'\s*--', str) is not None

    def _isUnitLine(self, str):
        return SchemaToMeta._unitLine.search(str) is not None

    def _isUcdLine(self, str):
        return SchemaToMeta._ucdLine.search(str) is not None

    def _retrUnit(self, str):
        x = SchemaToMeta._unitLine.search(str)
        return x.group(1)

    def _retrUcd(self, str):
        x = SchemaToMeta._ucdLine.search(str)
        return x.group(1)

    def _containsDescrTagStart(self, str):
        return re.search(r'<descr>', str) is not None

    def _containsDescrTagEnd(self, str):
        return re.search(r'</descr>', str) is not None

    def _retrDescr(self, str):
        x = SchemaToMeta._descrLine.search(str)
        return x.group(1)

    def _retrDescrStart(self, str):
        x = SchemaToMeta._descrStart.search(str)
        return x.group(1)

    def _retrDescrMid(self, str):
        x = SchemaToMeta._descrMiddle.search(str)
        return x.group(1)

    def _retrDescrEnd(self, str):
        if re.search(r'-- </descr>', str):
            return ''
        x = SchemaToMeta._descrEnd.search(str)
        return x.group(1)

    def _retrIsNotNull(self, str):
        if re.search(r'NOT NULL', str):
            return '1'
        return '0'

    def _retrType(self, str):
        arr = str.split()
        t = arr[1]
        if t == "FLOAT(0)":
            return "FLOAT"
        return t

    def _retrDefaultValue(self, str):
        if ' DEFAULT ' not in str:
            return None
        arr = str.split()
        returnNext = 0
        for a in arr:
            if returnNext:
                return a.rstrip(',')
            if a == 'DEFAULT':
                returnNext = 1

    # example strings:
    # "    PRIMARY KEY (id),",
    # "    KEY IDX_sId (sId ASC),",
    # "    KEY IDX_d (decl DESC)",
    # "    UNIQUE UQ_AmpMap_ampName(ampName)"
    # "    UNIQUE UQ_x(xx DESC, yy),"

    def _retrColumns(self, str):
        xx = re.search(r'[\s\w_]+\(([\w ,]+)\)', str.rstrip())
        xx = xx.group(1).split() # skip " ASC", " DESC" etc
        s = ''
        for x in xx:
            if not x == 'ASC' and not x == 'DESC':
                s += x
                if x[-1] == ',':
                    s += ' '
        return s

###############################################################################
def printIt():
    x = SchemaToMeta('/home/becla/dataArchDev/repos/cat/sql/baselineSchema.sql')
    t = x.parse()
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(t)

#if __name__ == '__main__':
#    printIt()
