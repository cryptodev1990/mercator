# Mercator Snowflake Stuff

Some setup scripts for Mercator Snowflake. To date, these are related to configuring Snowflake shares.

The directory `./sql` contains scripts to configure roles and integrations for geofencer shares.

To create a new Snowflake share and ETL pipeline for geofencer exports for an organization, run

```shell
poetry shell
python -m mercator_snowflake.create_geofencer_share ORGANIZATION_ID SNOWFLAKE_ACCOUNT_ID
```

Variables for Snowflake configuration are set in environment variables which can be specified in the `.env`. See `mercator_snowflake.Settings` class for which settings are used.

Right now this only is tested (and works) for account `TGYFADZ.IY49898`, locator `IY49898`, region AWS us-east-2 (Ohio).
