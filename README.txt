# Useful link:
http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask

# To install flask:
sudo aptitude install python-flask

# To run some quick tests:

  # load the metaserv schema and load some dummy data
  ./tests/reinit.sh
  ./tests.reinit.py
  ./bin/metaServBackend.py regDb DC_W13_Stripe82 L2
  ./bin/metaServBackend.py regDb jacek_1mRows L3

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
