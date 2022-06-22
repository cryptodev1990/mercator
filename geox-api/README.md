GeoX API
=========

The Makefile is the documentation for now. Check the Makefile.

Deploys are on fly.io.

Frontend is in a sibling directory to this one.

``py-geolift`` is a Python module
``app`` is the FastAPI web app.

Maintenance notes
-----------------

This app is already connected to Redis but if that breaks do

``fly secrets set REDIS_CONNECTION=redis://:<Get this from one password>@geox-redis.fly.dev/0``

geox-redis is not accessible to the public internet.
