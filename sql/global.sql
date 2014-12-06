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

-- LSST Database Schema for Metadata Store, global tables.


CREATE TABLE User 
    -- <descr>Basic information about every registered user. This is 
    -- a global table, (there is only one in the entire Metadata Store).
    -- Credentials are handled separately.</descr>
(
    userId INT NOT NULL AUTO_INCREMENT,
    firstName VARCHAR(64),
    lastName VARCHAR(64),
    affiliation VARCHAR(64),
    accessLevel ENUM('default', 'admin'),
    dbLimit INT,
        -- <descr>Database storage limit, in GB.</descr>
    fsLimit INT,
        -- <descr>File system storage limit, in GB.</descr>
    queryLoadLimit_h INT,
        -- <descr>Query load limit. Each query will have a "cost"
        -- associated with it. This limit is per hour. -1 = unlimited.
        -- </descr>
    queryLoadLimit_h INT,
        -- <descr>Query load limit. Each query will have a "cost"
        -- associated with it. This limit is per 24h. -1 = unlimited.
        -- </descr>
    PRIMARY KEY User_userId(userId)
) ENGINE = InnoDB;
 
-- Question: should we model groups here???
 
 
CREATE TABLE Repo
    -- <descr>Information about repositories, one row per repo.
    -- A repository can be a database, a directory with files.
    -- This is a global table, (there is only one in the entire Metadata Store).
    -- </descr>
(
    repoId INT NOT NULL AUTO_INCREMENT,
    url VARCHAR(255),
        -- <descr>Virtual location.</descr>
    project VARCHAR(64),
        -- <descr>Project name, e.g. LSST, SDSS, GAIA</descr>
    repoType ENUM('db', 'fits', 'config', 'custom'),
    dataRelease TINYINT,
        <descr>Data Release number, if applicable.</descr>
    version VARCHAR(255),
    sizeOnDisk BIGINT,
        -- <descr>Size in bytes.</descr>
    description VARCHAR(255),
    owner INT,
        -- <descr> references entry in User table</descr>
    createTime DATETIME,
    uploadTime DATETIME,
    priorityLevel ENUM('scratch', 'keepShort', 'keepLong'),
        -- <descr>This will be useful when purging.</descr>
    availability ENUM('published', 'notPublished'),
        -- <descr>I am sure there are many more states we can come up
        -- with.</descr>
    accessibility ENUM('public', 'private'),
        -- <descr>If we want to do in that direction, we'd need to cover
        -- group access too.</descr>
    backupStatus ENUM('requested', 'ongoing', 'notBackedUp'),
    lastBackup DATETIME,
        -- <descr>Time of the completion of the last successful backup.
        -- </descr>
    PRIMARY KEY repo_repoId(repoId)
) ENGINE = InnoDB;
 
 
CREATE TABLE RepoAnnotations
    -- <descr>Annotations for entries in Repo, in key-value form.
    -- This is a global table, (there is only one in the entire Metadata Store).
    -- </descr>
(
    repoId INT NOT NULL,
        -- <descr>References entry in Repo table.</descr>
    userId INT NOT NULL,
        -- <descr>User who entered given annotation. References entry in
        -- User table.</descr>
    key VARCHAR(64) NOT NULL,
    value TEXT NOT NULL,
    INDEX IDX_RepoAnnotations_repoId(repoId),
    INDEX IDX_RepoAnnotations_userId(userId)
) ENGINE = InnoDB;
 
 
CREATE TABLE FileRepo
    -- <descr>Information about file repositories. One row per file repo.
    -- This is a global table, (there is only one in the entire Metadata Store).
    -- </descr>
( 
    fileRepoId INT,
    fileCount INT,
        -- <descr>Number of files in the repo.</descr>
    fileType ENUM('fits', 'config', 'csv', 'tcv', 'custom'),
 
    PRIMARY KEY FileRepo_fileRepoId(fileRepoId)
) ENGINE = InnoDB;
 
 
CREATE TABLE FileRepoTypes
    -- <descr>Information about types of files in a file repository. 
    -- This is a global table, (there is only one in the entire Metadata Store).
    -- </descr>
( 
    fileRepoId INT,
        -- <descr>References an entry in FileRepo
    fileCount INT,
        -- <descr>Number of files in the repo.</descr>
    fileType ENUM('fits', 'config', 'csv', 'tcv', 'custom'),
 
    INDEX KEY IDX_FileRepoTypes_fileRepoId(fileRepoId)
) ENGINE = InnoDB;
 
 
 
-- FileRepoAnnotations, similar to RepoAnnotations goes here...
