# geox

## References

- [FastAPI](https://github.com/tiangolo/fastapi)

## Useful links

- [Auth0 Dashboard](https://manage.auth0.com/dashboard/us/dev-w40e3mxg/)
- [Fly.io Dashboard](https://fly.io/dashboard/geox)
- [Vercel Dashboard](https://vercel.com/quincy-s/geox)

## Pre-commit hooks

The repo includes a few universal git pre-commit hooks that will help avoid some common errors before
you commit and commiting large files.

The file `.pre-commit-config.yaml` includes a

To use.

1. Follow instructions at [pre-commit.com](https://pre-commit.com/) to install pre-commit.
   If you are using MacOS this is,

   ```shell
   brew install pre-commit
   ```

2. Install the pre-commit hooks to your local repo by running the following command in the repo root directory:

   ```shell
   pre-commit
   ```

If you need or want to ignore some pre-commit checks, you can use git's `--no-verify` option to ignore all pre-commit hooks,

```shell
git commit --no-verity -m "foo"
```

or set the `SKIP` shell variable to skip only a subset of pre-commit hooks,

```shell
SKIP=check-secrets,check-added-large-files git commit -m "foo"
```
