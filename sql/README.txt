# handy for testing:
mysql -e "drop database metaServ; create database metaServ"
mysql metaServ < global.sql
mysql metaServ < dbRepo.sql
mysql metaServ < fileRepo.sql 
