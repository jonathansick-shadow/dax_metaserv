# To run some quick tests:

  # load the metaserv schema and load some data
  # note, examples/quickTest requires cat module checked out in ../ directory
  ./bin/resetDb.sh
  ./bin/metaBackend.py < examples/quickTest

  # run the server
  python bin/metaServer.py

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
