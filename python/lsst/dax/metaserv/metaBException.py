#!/usr/bin/env python

# LSST Data Management System
# Copyright 2015 LSST Corporation.
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
Exception for MetaServ Backend.

@author  Jacek Becla, SLAC

"""

from lsst.db.exception import produceExceptionClass

MetaBException = produceExceptionClass('MetaBException', [
    (3005, "BAD_CMD", "Bad command, see HELP for details."),
    (3010, "DB_DOES_NOT_EXIST", "Database does not exist."),
    (3015, "NOT_MATCHING", "Schema from db and ascii file do not match."),
    (3020, "TB_NOT_IN_DB", "Table not found in the database."),
    (3025, "COL_NOT_IN_TB", "Column not found in the table."),
    (3030, "COL_NOT_IN_FL", "Column not found in the ascii file."),
    (3035, "OWNER_NOT_FOUND", "Owner not found."),
    (3040, "PROJECT_EXISTS", "Project already exists."),
    (3045, "PROJECT_NOT_FOUND", "Project not found."),
    (3050, "INST_EXISTS", "Institution already exists.."),
    (3055, "INST_NOT_FOUND", "Institution not found."),
    (9998, "NOT_IMPLEMENTED", "Feature not implemented yet."),
    (9999, "INTERNAL", "Internal error.")])
