GeoX API
=========

The Makefile is the documentation for now. Check the Makefile.

Deploys are on fly.io.

Frontend is in a sibling directory to this one.

``py-geolift`` is a Python module
``app`` is the FastAPI web app.

Local Install
-------------

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

This make command should install the necessary dependencies.

```shell
make dev-install
```


Copy the `.env.template` file to `.env.local` and fill in the values

```shell
cp .env.template .env.local
```


Docker Install
---------------

Define the relevant ENV variables in `.env.docker`.

For dev work, this will start the app running on `localhost:8080`.
```
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

Changes made to files in the directory will be reloaded.
However, if new python requirements are added, the image needs to be rebuilt.

For prod, this will start the app:
```
docker-compose -f docker-compose.yml up
```
