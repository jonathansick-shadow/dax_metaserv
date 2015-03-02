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

-- @brief LSST Database Schema for Metadata Store, global tables.
--
-- @author Jacek Becla, SLAC


CREATE TABLE User
    -- <descr>Basic information about every registered user. This is
    -- a global table, (there is only one in the entire Metadata Store).
    -- Credentials are handled separately. Ultimately this will be managed
    -- through LDAP.</descr>
(
    userId INT NOT NULL AUTO_INCREMENT,
        -- <descr>Unique identifier.</descr>
    mysqlUserName VARCHAR(64),
        -- <descr>MySQL user name.</descr>
    firstName VARCHAR(64),
    lastName VARCHAR(64),
    email VARCHAR(64),
    instId INT,
        -- <descr>Id of the institution the user is affiliated with.</descr>
    PRIMARY KEY PK_User_userId(userId),
    UNIQUE UQ_User_mysqlUserName(mysqlUserName)
) ENGINE = InnoDB;

CREATE TABLE Institution
    -- <descr>Institutions.</descr>
(
    instId INT NOT NULL AUTO_INCREMENT,
        -- <descr>Unique identifier.</descr>
    instName VARCHAR(64),
    PRIMARY KEY PK_Institution_instId(instId),
    UNIQUE UQ_Institution_instName(instName)
) ENGINE = InnoDB;

CREATE TABLE Project
    -- <descr>Projects, for which we have data sets tracked by metaserv</descr>
(
    projectId INT NOT NULL AUTO_INCREMENT,
        -- <descr>Unique identifier.</descr>
    projectName VARCHAR(64),
    PRIMARY KEY PK_Project_projectId(projectId),
    UNIQUE UQ_Project_projectName(projectName)
) ENGINE = InnoDB;

CREATE TABLE User_Authorization
    -- <descr>Per-user authorization.</descr>
(
    userId INT NOT NULL,
        -- <descr>Id of the user for who given authorization is defined.</descr>
    accessLevel ENUM('default', 'admin'),
    dbLimit INT,
        -- <descr>Database storage limit, in GB.</descr>
    fsLimit INT,
        -- <descr>File system storage limit, in GB.</descr>
    queryLoadLimit_h INT,
        -- <descr>Query load limit. Each query will have a "cost"
        -- associated with it. This limit is per hour. -1 = unlimited.
        -- </descr>
    INDEX IDX_UserAuth_userId(userId)
) ENGINE = InnoDB;


CREATE TABLE Groups
   -- <descr>Basic information about every group.</descr>
(
    groupId INT NOT NULL AUTO_INCREMENT,
        -- <descr>Unique identifier.</descr>
    groupName VARCHAR(64),
    PRIMARY KEY PK_Group_groupId(groupId)

) ENGINE = InnoDB;


CREATE TABLE Group_Authorization
    -- <descr>Per-group authorization.</descr>
(
    groupId INT NOT NULL
        -- <descr>Id of the group for which given authorization is defined.
        -- </descr>
) ENGINE = InnoDB;


CREATE TABLE User_To_Group
    -- <descr>Definition of which user belongs to which group.</descr>
(
    userId INT NOT NULL,
        -- <descr>Id of the user.-- </descr>
    groupId INT NOT NULL,
        -- <descr>Id of the group.-- </descr>
    INDEX IDX_UserToGroup_userId(userId),
    INDEX IDX_UserToGroup_groupId(groupId)
) ENGINE = InnoDB;


CREATE TABLE Repo
    -- <descr>Information about repositories, one row per repo.
    -- A repository can be a database, a directory with files.
    -- This is a global table, (there is only one in the entire Metadata Store).
    -- </descr>
(
    repoId INT NOT NULL AUTO_INCREMENT,
    url VARCHAR(255),
        -- <descr>Virtual location.</descr>
    projectId INT,
        -- <descr>Id of the project this data set comes from. References an entry
        -- in the Project table.</descr>
    repoType ENUM('db', 'butler', 'file', 'custom'),
    lsstLevel ENUM ('DC', 'L1', 'L2', 'L3', 'dev'),
        -- <descr>Supported levels: DC ('Data Challenge'), L1 ('Level 1 / Alert
        -- Production'), L2 ('Level 2 / Data Release'), L3 ('Level 3 / User data'),
        -- dev ('unclassified development')</descr>
    dataRelease VARCHAR(64),
        -- <descr>Data Release, if applicable.</descr>
    version VARCHAR(255),
    shortName VARCHAR(255),
    description VARCHAR(255),
    ownerId INT,
        -- <descr>References entry in User table</descr>
    checksum VARCHAR(128),
    createTime DATETIME,
    ingestTime DATETIME,
    priorityLevel ENUM('scratch', 'keepShort', 'keepLong'),
        -- <descr>This will be useful when purging.</descr>
    availability ENUM('loading', 'published', 'notPublished', 'locked4Maintenance'),
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
        -- </ul></descr>
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
    theKey VARCHAR(64) NOT NULL,
    theValue TEXT NOT NULL,
    INDEX IDX_RepoAnnotations_repoId(repoId),
    INDEX IDX_RepoAnnotations_userId(userId)
) ENGINE = InnoDB;


CREATE TABLE FileRepo
    -- <descr>Information about file repositories. One row per file repo.
    -- This is a global table, (there is only one in the entire Metadata Store).
    -- </descr>
(
    repoId INT,
        -- <descr>References an entry in Repo.</descr>

    -- can't think of things to put in there right now, but I am sure
    -- we will identify these things...

    PRIMARY KEY FileRepo_repoId(repoId)
) ENGINE = InnoDB;


CREATE TABLE FileRepoTypes
    -- <descr>Information about types of files in a file repository.
    -- This is a global table, (there is only one in the entire Metadata Store).
    -- </descr>
(
    repoId INT,
        -- <descr>References an entry in FileRepo.</descr>
    fileType ENUM('fits', 'config', 'csv', 'tcv', 'custom'),
    fileCount INT,
        -- <descr>Number of files in the repo.</descr>
    INDEX IDX_FileRepoTypes_repoId(repoId)
) ENGINE = InnoDB;



-- FileRepoAnnotations, similar to RepoAnnotations goes here...
