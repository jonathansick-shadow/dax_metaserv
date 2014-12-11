-- LSST Data Management System
-- Copyright 2008-2014 AURA/LSST.
-- 
-- This product includes software developed by the
-- LSST Project (http://www.lsst.org/).
--
-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
-- 
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
-- 
-- You should have received a copy of the LSST License Statement and 
-- the GNU General Public License along with this program.  If not, 
-- see <https://www.lsstcorp.org/LegalNotices/>.

-- LSST Database Schema for Metadata Store, database-repository related.


CREATE TABLE DbMeta
    -- <descr>Information about one file. One row per file.</descr>
(
    dbMetaId INT NOT NULL AUTO_INCREMENT,
        -- <descr>Unique identifier.</descr>
        -- <ucd>meta.id</ucd>
    dbName VARCHAR(64),
        -- <descr>The name of the database.</descr>
    PRIMARY KEY DbMeta_dbMetaId(dbMetaId)
) ENGINE=InnoDB;
 

CREATE TABLE DDT_Table
    -- <descr>A Data Definition Table. Augments standard MySQL-managed metadata.
    -- This is for table-level metadata.</descr>
(
    tableId INT NOT NULL AUTO_INCREMENT,
        -- <descr>Unique identifier.</descr>
        -- <ucd>meta.id</ucd>
    dbMetaId INT NOT NULL,
        -- <descr>References entry in DbMeta - database where this table
        -- belongs.</descr>
    tableName VARCHAR(64),
        -- <descr>The name of the table.</descr>
    descr TEXT,
        -- <descr>Table description.</descr>
) ENGINE=InnoDB;


CREATE TABLE DDT_Column
    -- <descr>A Data Definition Table. Augments standard MySQL-managed metadata.
    -- This is for column-level metadata.</descr>
(
    columnId INT NOT NULL AUTO_INCREMENT,
        -- <descr>Unique identifier.</descr>
        -- <ucd>meta.id</ucd>
    columnName VARCHAR(64),
        -- <descr>The name of the column.</descr>
    tableId INT NOT NULL AUTO_INCREMENT,
        -- <descr>References entry in DDT_Table - table where this column
        -- belongs.</descr>
    descr TEXT,
        -- <descr>Column description.</descr>
    ucd VARCHAR(1024),
        -- <descr> UCD definitions for a given column. Based on:
        -- http://www.ivoa.net/Documents/cover/UCDlist-20070402.html.</descr>
    units VARCHAR(64),
        -- <descr>Description of units for a given column.</descr>
    SUI_displayPrec INT,
        -- <descr>Display precision, for SUI.</descr>
    SUI_displayCol BOOL DEFAULT True,
        -- <descr>A flag whether to display this column or not by default.</descr>
) ENGINE=InnoDB;
