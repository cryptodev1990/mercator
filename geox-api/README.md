GeoX API
=========

The Makefile is the documentation for now. Check the Makefile.

Deploys are on fly.io.

Frontend is in a sibling directory to this one.

``py-geolift`` is a Python module
``app`` is the FastAPI web app.

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

This make command should install the necessary dependencies.

```shell
make dev-install
```


Copy the `.env.template` file to `.env.local` and fill in the values

```shell
cp .env.template .env.local
```
