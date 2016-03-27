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

Note that the SchemaToMeta expects the input file to be structured in certain
way, e.g., it will not parse any sql-compliant structure. A comprehensive
set of examples can be found in the tests/testSchemaToMeta.py.
In addition, the cat/sql/baselineSchema.py is a good "template".

This code was originally written for schema browser
(in cat/bin/schema_to_metadata.py).
"""

_tableStart = re.compile(r'CREATE TABLE (\w+)')
_tableEnd = re.compile(r"\)")
_engineLine = re.compile(r'\)\s*(ENGINE|TYPE)\s*=[\s]*(\w+)\s*;')
_columnLine = re.compile(r'\s*(\w+)\s+\w+')
_idxCols = re.compile(r'\((.+?)\)')
_unitLine = re.compile(r'<unit>(.+)</unit>')
_ucdLine = re.compile(r'<ucd>(.+)</ucd>')
_descrLine = re.compile(r'<descr>(.+)</descr>')
_descrStart = re.compile(r'<descr>(.+)')
_descrMiddle = re.compile(r'--(.+)')
_descrEnd = re.compile(r'--(.*)</descr>')
_commentLine = re.compile(r'\s*--')
_defaultLine = re.compile(r'\s+DEFAULT\s+(.+?)[\s,]')

####################################################################################
# Helper functions
####################################################################################


def _isIndexDefinition(c):
    return c in ["PRIMARY", "KEY", "INDEX", "UNIQUE"]


def _isCommentLine(theString):
    return _commentLine.match(theString) is not None


def _isUnitLine(theString):
    return _unitLine.search(theString) is not None


def _isUcdLine(theString):
    return _ucdLine.search(theString) is not None


def _retrUnit(theString):
    return _unitLine.search(theString).group(1)


def _retrUcd(theString):
    return _ucdLine.search(theString).group(1)


def _containsDescrTagStart(theString):
    return '<descr>' in theString


def _containsDescrTagEnd(theString):
    return '</descr>' in theString


def _retrDescr(theString):
    return _descrLine.search(theString).group(1)


def _retrDescrStart(theString):
    return _descrStart.search(theString).group(1)


def _retrDescrMid(theString):
    return _descrMiddle.search(theString).group(1)


def _retrDescrEnd(theString):
    return _descrEnd.search(theString).group(1).rstrip()


def _retrIsNotNull(theString):
    return 'NOT NULL' in theString


def _retrType(theString):
    t = theString.split()[1].rstrip(',')
    return "FLOAT" if t == "FLOAT(0)" else t


def _retrDefaultValue(theString):
    if not _defaultLine.search(theString):
        return None
    arr = theString.split()
    returnNext = 0
    for a in arr:
        if returnNext:
            return a.rstrip(',')
        if a == 'DEFAULT':
            returnNext = 1


def _retrIdxColumns(theString):
    colExprs = _idxCols.search(theString).group(1).split(',')
    columns = [" ".join([word for word in expr.split()
                         if word not in ('ASC', 'DESC')]) for expr in colExprs]
    return ", ".join(columns)

####################################################################################
# The parseSchema function
####################################################################################


def parseSchema(inFName):
    """Do actual parsing. Returns the retrieved structure as a table. The
    structure of the produced table:
{ <tableName1>: {
    'columns': [ { 'defaultValue': <value>,
                   'description': <column description>,
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

    if not os.path.isfile(inFName):
        sys.stderr.write("File '%s' does not exist\n" % inFName)
        sys.exit(1)

    in_table = None
    in_col = None
    in_colDescr = None
    table = {}

    colNum = 1

    iF = open(inFName, mode='r')
    for line in iF:
        m = _tableStart.search(line)
        if m is not None and not _isCommentLine(line):
            tableName = m.group(1)
            table[tableName] = {}
            colNum = 1
            in_table = table[tableName]
            in_col = None
        elif _tableEnd.match(line):
            m = _engineLine.match(line)
            if m is not None:
                engineName = m.group(2)
                in_table["engine"] = engineName
            in_table = None
        elif in_table is not None:  # process columns for given table
            m = _columnLine.match(line)
            if m is not None:
                firstWord = m.group(1)
                if _isIndexDefinition(firstWord):
                    t = "-"
                    if firstWord == "PRIMARY":
                        t = "PRIMARY KEY"
                    elif firstWord == "UNIQUE":
                        t = "UNIQUE"
                    idxInfo = {"type": t,
                               "columns": _retrIdxColumns(line)
                               }
                    in_table.setdefault("indexes", []).append(idxInfo)
                else:
                    in_col = {"name": firstWord,
                              "displayOrder": str(colNum),
                              "type": _retrType(line),
                              "notNull": _retrIsNotNull(line),
                              }
                    dv = _retrDefaultValue(line)
                    if dv is not None:
                        in_col["defaultValue"] = dv
                    colNum += 1
                    if "columns" not in in_table:
                        in_table["columns"] = []
                    in_table["columns"].append(in_col)
            elif _isCommentLine(line):  # handle comments
                if in_col is None:    # table comment

                    if _containsDescrTagStart(line):
                        if _containsDescrTagEnd(line):
                            in_table["description"] = _retrDescr(line)
                        else:
                            in_table["description"] = _retrDescrStart(line)
                    elif "description" in in_table:
                        if _containsDescrTagEnd(line):
                            in_table["description"] += _retrDescrEnd(line)
                        else:
                            in_table["description"] += _retrDescrMid(line)
                else:
                                      # column comment
                    if _containsDescrTagStart(line):
                        if _containsDescrTagEnd(line):
                            in_col["description"] = _retrDescr(line)
                        else:
                            in_col["description"] = _retrDescrStart(line)
                            in_colDescr = 1
                    elif in_colDescr:
                        if _containsDescrTagEnd(line):
                            in_col["description"] += _retrDescrEnd(line)
                            in_colDescr = None
                        else:
                            in_col["description"] += _retrDescrMid(line)

                            # units
                    if _isUnitLine(line):
                        in_col["unit"] = _retrUnit(line)

                        # ucds
                    if _isUcdLine(line):
                        in_col["ucd"] = _retrUcd(line)

    iF.close()
    return table


###############################################################################
def printIt():
    t = parseSchema('../cat/sql/baselineSchema.sql')
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(t)

# if __name__ == '__main__':
#    printIt()
