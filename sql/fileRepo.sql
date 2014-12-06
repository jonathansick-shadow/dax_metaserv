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

-- LSST Database Schema for Metadata Store, file-repository related.


CREATE TABLE FileMeta
    -- <descr>Information about one file. One row per file.</descr>
(
    fileMetaId INT NOT NULL AUTO_INCREMENT,
    checksum VARCHAR(64),
    createTime DATETIME,
    uploadTime DATETIME,
    size BIGINT,
        -- <descr>File size in bytes.</descr>
    PRIMARY KEY FileMeta_fileMetaId(fileMetaId)
) ENGINE = InnoDB;
 
 
-- FileMetaAnnotations, similar to RepoAnnotations goes here...
 
 
CREATE TABLE FitsMeta
    -- <descr>Table of basic FITS file information. Name, location,
    -- number of HDUs.</descr>
(
    fitsFileId BIGINT NOT NULL AUTO_INCREMENT,
    fileName   VARCHAR(255) NOT NULL,
    hdus       TINYINT      NOT NULL,
    PRIMARY KEY (fitsFileId)
) ENGINE=InnoDB;
 
CREATE TABLE FitsKeyValues
    -- <descr>Table of FITS keyword and value pairs. </decr>
(
    fitsFileId  BIGINT      NOT NULL,
    fitsKey     VARCHAR(8)  NOT NULL,
    hdu         TINYINT     NOT NULL,
    stringValue VARCHAR(90),
    intValue    INTEGER,
    doubleValue DOUBLE,
    INDEX IDX_fitsKeyVal_fitsFileId (fitsFileId),
    INDEX IDX_fitsKeyVal_fitsKey (fitsKey)
) ENGINE=InnoDB;
 
 
CREATE TABLE FitsPositions
    -- <descr>Table of RA and Dec position and exposure time.</descr>
(
    fitsFileId BIGINT  NOT NULL,
    hdu        TINYINT NOT NULL,
    equinox    DOUBLE,
    pdec       DOUBLE,
    pra        DOUBLE,
    rotang     DOUBLE,
    pdate      TIMESTAMP,
    INDEX IDX_fitsPos_fitsFileId (fitsFileId),
    INDEX IDX_fitsPos_date (pdate),
    INDEX IDX_fitsPos_ra (pra),
    INDEX IDX_fitsPos_dec (pdec)
) ENGINE=InnoDB;
 
 
ALTER TABLE FitsKeyValues ADD CONSTRAINT FK_fitsKeyVal_fitsFileId
    FOREIGN KEY (fitsFileId) REFERENCES FitsFiles (fitsFileId);
 
ALTER TABLE FitsPositions ADD CONSTRAINT FK_fitsPos_fitsFileId
    FOREIGN KEY (fitsFileId) REFERENCES FitsFiles (fitsFileId);
 
