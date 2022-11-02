"""
CLI to manipulate shapes, users, namespaces, and other contents
of our database through the CRUD functions (though not the web API itself)

This is useful for debugging, testing, and the occasional
manual data manipulation.
"""
import argparse
import sys
from asyncio import get_event_loop

from app.core.config import get_settings
from cli.programs import cli_apps

settings = get_settings()

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
subparsers.required = True
for app in cli_apps:
    app.generate_cli(subparsers)


if __name__ == "__main__":
    loop = get_event_loop()

    for app in cli_apps:
        args = parser.parse_args()
        app_name = sys.argv[1]
        if app_name == app.APP_NAME:
            app.run_from_cli(subparsers, args, loop)
            break
