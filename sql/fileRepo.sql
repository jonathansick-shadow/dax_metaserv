-- LSST Data Management System
-- Copyright 2014-2015 AURA/LSST.
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

-- @brief LSST Database Schema for Metadata Store, file-repository related.
--
-- @author Jacek Becla, SLAC


CREATE TABLE File
    -- <descr>Information about one file. One row per file.</descr>
(
    fileId INT NOT NULL AUTO_INCREMENT,
    repoId INT NOT NULL,
        -- <descr>Id of the repo this file belongs to.</descr>
    fileName VARCHAR(255) NOT NULL,
    url VARCHAR(255),
        -- <descr>Virtual location.</descr>
    checksum VARCHAR(128),
    createTime DATETIME,
    ingestTime DATETIME,
    size BIGINT,
        -- <descr>File size in bytes.</descr>
    availability ENUM('published', 'notPublished'),
        -- <descr>I am sure there are many more states we can come up
        -- with.</descr>
    accessibility ENUM('public', 'private'),
        -- <descr>If we want to do in that direction, we'd need to cover
        -- group access too.</descr>
    onDisk BOOL,
        -- <descr>Bitwise OR describing locations
        -- <ul>
        --    <li>0x1: in memory only
        --    <li>0x2: on ssd
        --    <li>0x4: on spinning disk
        --    <li>0x8: on tape
        --  </ul></descr>
    backupStatus ENUM('requested', 'ongoing', 'notBackedUp'),
    lastBackup DATETIME,
        -- <descr>Time of the completion of the last successful backup.
        -- </descr>
    PRIMARY KEY PK_File_fileId(fileId)
) ENGINE = InnoDB;
 

CREATE TABLE FileAnnotations
    -- <descr>Annotations for entries in File, in key-value form.-- </descr>
(
    fileId INT NOT NULL,
        -- <descr>References entry in File table.</descr>
    userId INT NOT NULL,
        -- <descr>User who entered given annotation. References entry in
        -- User table.</descr>
    theKey VARCHAR(64) NOT NULL,
    theValue TEXT NOT NULL,
    INDEX IDX_FileAnnotations_repoId(fileId),
    INDEX IDX_FileAnnotations_userId(userId)
) ENGINE = InnoDB;
 
 
CREATE TABLE FitsMeta
    -- <descr>FITS-file specific information.</descr>
(
    fileId BIGINT NOT NULL,
        -- <descr>Id of the corresponding entry in File table.</descr>
    hdus TINYINT NOT NULL,
    PRIMARY KEY PK_FitsMeta_fileId(fileId)
) ENGINE=InnoDB;


CREATE TABLE FitsStructuredMeta
    -- <descr>FITS-file specific structured metadata.</descr>
(
    fileId BIGINT NOT NULL,
    hdu TINYINT NOT NULL,
    equinox DOUBLE,
    ra DOUBLE NOT NULL,
        -- <descr>Ra of amp center.</descr>
        -- <ucd>pos.eq.ra</ucd>
        -- <unit>deg</unit>
    decl DOUBLE NOT NULL,
        -- <descr>Decl of amp center.</descr>
        -- <ucd>pos.eq.dec</ucd>
        -- <unit>deg</unit>
    rotAng DOUBLE,
    obsStart TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        -- <descr>Start of the exposure, TAI, accurate to 10ms.</descr>
        -- <ucd>time.start</ucd>
    expMidpt DOUBLE NOT NULL,
        -- <descr>Midpoint for exposure. TAI, accurate to 10ms.</descr>
        -- <ucd>time.epoch</ucd>
    expTime DOUBLE NOT NULL,
        -- <descr>Duration of exposure, accurate to 10ms.</descr>
        -- <ucd>time.duration</ucd>
        -- <unit>s</unit>
    INDEX IDX_fitsStructuredMeta_fileId(fileId),
    INDEX IDX_fitsStructuredMeta_ra(ra),
    INDEX IDX_fitsStructuredMeta_decl(decl)
) ENGINE=InnoDB;


CREATE TABLE FitsUnstructuredMeta
    -- <descr>FITS-file specific unstructured metadata
    -- (key/value pairs).</descr>
(
    fileId BIGINT NOT NULL,
        -- <descr>Id of the corresponding entry in File table.</descr>
    fitsKey VARCHAR(8) NOT NULL,
    hdu TINYINT NOT NULL,
    stringValue VARCHAR(90),
    intValue INTEGER,
    doubleValue DOUBLE,
    INDEX IDX_fitsUnstructuredMeta_fitsFileId(fileId),
    INDEX IDX_fitsUnstructuredMeta_fitsKey(fitsKey)
) ENGINE=InnoDB;


# todo
#ALTER TABLE FitsKeyValues ADD CONSTRAINT FK_fitsKeyVal_fitsFileId
#    FOREIGN KEY (fitsFileId) REFERENCES FitsFiles(fitsFileId);
# 
#ALTER TABLE FitsPositions ADD CONSTRAINT FK_fitsPos_fitsFileId
#    FOREIGN KEY (fitsFileId) REFERENCES FitsFiles(fitsFileId);
 
