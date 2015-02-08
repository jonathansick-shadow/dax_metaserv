#!/bin/bash

mysql --host lsst10 -u metaServ -p -e "drop   database metaServ_core"
mysql --host lsst10 -u metaServ -p -e "create database metaServ_core"
mysql --host lsst10 -u metaServ -p metaServ_core < sql/global.sql
mysql --host lsst10 -u metaServ -p metaServ_core < sql/dbRepo.sql
mysql --host lsst10 -u metaServ -p metaServ_core < sql/fileRepo.sql
