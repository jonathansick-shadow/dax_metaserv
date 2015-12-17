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

-- @brief LSST Database Schema for Metadata Store, tables containing
-- information about users, groups they belong to, and authorizations.
--
-- @author Jacek Becla, SLAC

CREATE TABLE Institution
    -- <descr>Institutions.</descr>
(
    instId INT NOT NULL AUTO_INCREMENT,
        -- <descr>Unique identifier.</descr>
    instName VARCHAR(64),
    PRIMARY KEY PK_Institution_instId(instId),
    UNIQUE UQ_Institution_instName(instName)
) ENGINE = InnoDB;


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
    UNIQUE UQ_User_mysqlUserName(mysqlUserName),
    CONSTRAINT FK_Institution_instId
        FOREIGN KEY(instId)
        REFERENCES Institution(instId)
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
    INDEX IDX_UserAuth_userId(userId),
    CONSTRAINT FK_UserAuth_userId
        FOREIGN KEY(userId)
        REFERENCES User(userId)
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
    groupId INT NOT NULL,
        -- <descr>Id of the group for which given authorization is defined.
        -- </descr>
    CONSTRAINT FK_GroupAuth_groupId
        FOREIGN KEY(groupId)
        REFERENCES Groups(groupId)
) ENGINE = InnoDB;


CREATE TABLE User_To_Group
    -- <descr>Definition of which user belongs to which group.</descr>
(
    userId INT NOT NULL,
        -- <descr>Id of the user.-- </descr>
    groupId INT NOT NULL,
        -- <descr>Id of the group.-- </descr>
    INDEX IDX_UserToGroup_userId(userId),
    INDEX IDX_UserToGroup_groupId(groupId),
    CONSTRAINT FK_UserToGroup_userId
        FOREIGN KEY(userId)
        REFERENCES User(userId),
    CONSTRAINT FK_UserToGroup_groupId
        FOREIGN KEY(groupId)
        REFERENCES Groups(groupId)
) ENGINE = InnoDB;

CREATE TABLE User_To_Project
    -- <descr>Definition of which user belongs to which project.</descr>
(
    userId INT NOT NULL,
        -- <descr>Id of the user.-- </descr>
    projectId INT NOT NULL,
        -- <descr>Id of the project.-- </descr>
    INDEX IDX_UserToProject_userId(userId),
    INDEX IDX_UserToProject_projectId(projectId),
    CONSTRAINT FK_UserToProject_userId
        FOREIGN KEY(userId)
        REFERENCES User(userId),
    CONSTRAINT FK_UserToProject_projectId
        FOREIGN KEY(projectId)
        REFERENCES Project(projectId)
) ENGINE = InnoDB;
