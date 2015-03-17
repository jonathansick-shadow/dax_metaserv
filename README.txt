# To run some quick tests:

  # setup the metaserv module for use
  setup -k -r .

  # identify mysql server to use, and appropriete mysql account, the server
  # should be up and running

  # prepare mysql auth files ~/.lsst/dbAuth-dbServ.txt and ~/.lsst/dbAuth-metaServ.txt
  # an example can be found in bin/resetDb.sh

  # load the metaserv schema and load some data
  # note, examples/quickTest requires cat module checked out in ../ directory
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
