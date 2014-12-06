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
   -- tbd what else
    -- maybe info how to connect to that database?
) ENGINE=InnoDB;
 
CREATE TABLE DDT
    -- <descr>A Data Definition Table will be maintained to augment standard
    -- MySQL-managed metadata. DDT will contain: UI-specific information such 
    -- as display precision, or whether to display a given column by default.
    --  VO-compliance related metadata, such us UIDs for each column.</descr>
(
    tableName VARCHAR(64),

    -- more tbd
 
) ENGINE=InnoDB;
