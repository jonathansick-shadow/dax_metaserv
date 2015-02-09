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
  http://localhost:5000/meta
  http://localhost:5000/meta/v0
  http://localhost:5000/meta/v0/db
  http://localhost:5000/meta/v0/db/L2
  http://127.0.0.1:5000/meta/v0/db/L2/DC_W13_Stripe82/tables
  http://127.0.0.1:5000/meta/v0/db/L2/DC_W13_Stripe82/tables/Science_Ccd_Exposure/schema
