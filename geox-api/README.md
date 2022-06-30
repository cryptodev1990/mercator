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

Install
-------

On MacOS, install Postgresql and create the `geox` database.

```shell
brew install postgresql
brew services start postgresql
createdb geox
```

Check that you can connect to the `geox` database.

```shell
psql geox
```

Install redis and start redis

```shell
brew install redis
brew services start redis
```

If it is running, the output should look like this:

```browse
$ brew services info redis
redis (homebrew.mxcl.redis)
Running: ✔
Loaded: ✔
Schedulable: ✘
```

Which `make` commands need to run?

