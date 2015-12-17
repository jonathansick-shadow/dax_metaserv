# handy for testing:
mysql -e "drop database metaServ; create database metaServ"
mysql metaServ < userAuth.sql
mysql metaServ < repo.sql
mysql metaServ < dbRepo.sql
mysql metaServ < fileRepo.sql
