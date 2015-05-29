# To run some quick tests:

  # setup the metaserv module for use
  setup -k -r .

  # identify mysql server to use, and appropriete mysql account, the server
  # should be up and running

  # prepare mysql auth file ~/.lsst/dbAuth-metaServ.txt
  # an example can be found in bin/resetDb.sh

  # create your database, load schema
  # note, examples/quickTest requires cat module checked out in ../ directory
  # to learn about the structure of the ASCII schema file, refer to
  # metaserv/ddlStructure.md
  mysql --defaults-file=<yourAuth> -e "create database <yourUserName>_metaServ_baselineSchema"
  mysql --defaults-file=<yourAuth> <yourUserName>_metaServ_baselineSchema < ../cat/sql/baselineSchema.sql

  # edit examples/quickTest and enter yourUserName

  # load the metaserv schema and register that database
  ./bin/resetDb_dev.sh
  ./bin/metaAdmin.py < examples/quickTest

  # run the server
  ./bin/metaServer.py

  # and fetch the urls:
  curl http://localhost:5000/meta
  curl http://localhost:5000/meta/v0
  curl http://localhost:5000/meta/v0/db
  curl http://localhost:5000/meta/v0/db/L2
  curl http://127.0.0.1:5000/meta/v0/db/L2/DC_W13_Stripe82/tables
  curl http://127.0.0.1:5000/meta/v0/db/L2/DC_W13_Stripe82/tables/Science_Ccd_Exposure/schema

  curl -H accept:text/html http://localhost:5000/meta
  curl -H accept:text/html http://localhost:5000/meta/v0
  curl -H accept:text/html http://localhost:5000/meta/v0/db
  curl -H accept:text/html http://localhost:5000/meta/v0/db/L2
  curl -H accept:text/html http://127.0.0.1:5000/meta/v0/db/L2/DC_W13_Stripe82/tables
  curl -H accept:text/html http://127.0.0.1:5000/meta/v0/db/L2/DC_W13_Stripe82/tables/Science_Ccd_Exposure/schema
