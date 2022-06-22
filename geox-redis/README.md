Task runner
-----------

Dedicated task runner for GeoX

```
fly launch --image flyio/redis:6.2.6 --no-deploy --name geox-redis
fly volumes create redis_server --size 1
```

```
cat >> fly.toml <<TOML
  [[mounts]]
    destination = "/data"
    source = "redis_server"
TOML
```

`fly secrets set REDIS_PASSWORD=<see 1Password>`

See [here](https://fly.io/docs/reference/redis/).
