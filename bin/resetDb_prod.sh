#!/bin/sh

# This is for production environment.

# Use with caution, as this will completely wipe out and recreate the database
# metaServ_core in the database server described in the ~/.lsst/dbAuth-metaServ.txt
mysql --defaults-file=~/.lsst/dbAuth-dbServ.txt -e "drop database metaServ_core"
mysql --defaults-file=~/.lsst/dbAuth-dbServ.txt --database="" -e "create database metaServ_core"
mysql --defaults-file=~/.lsst/dbAuth-metaServ.txt < sql/global.sql
mysql --defaults-file=~/.lsst/dbAuth-metaServ.txt < sql/dbRepo.sql
mysql --defaults-file=~/.lsst/dbAuth-metaServ.txt < sql/fileRepo.sql

# example ~/.lsst/dbAuth-metaServ.txt
# [mysql]
# host     = lsst10.ncsa.illinois.edu
# port     = 3306
# user     = metaServ
# password = [password here]
# database = metaServ_core
