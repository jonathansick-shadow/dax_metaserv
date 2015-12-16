# handy for testing:
mysql -e "drop database metaServ; create database metaServ"
mysql metaServ < repo.sql
mysql metaServ < dbRepo.sql
mysql metaServ < fileRepo.sql
mysql metaServ < userAuth.sql
