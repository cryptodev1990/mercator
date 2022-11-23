"""Post-processes openapi.json

This script post-processes the openapi.json to produce valid typescript models
using `opeanpi-typescript-codegen`.
"""

import json
from pathlib import Path
from typing import Optional

import typer

from app.main import app


def main(output: Optional[Path] = typer.Option(None, exists=False)) -> None:
    """Generate an openapi schema to use in generating typescript clients."""
    schema = app.openapi()
    schema_str = json.dumps(schema, indent=2)
    if output:
        with output.open("w") as f:
            f.write(schema_str)
    else:
        typer.echo(schema_str)


if __name__ == "__main__":
    typer.run(main)
