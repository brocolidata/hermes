from pathlib import Path
from typing import Optional

import typer
from artefact_parser.main import parse_project
from typing_extensions import Annotated

app = typer.Typer()


@app.command()
def parse(
    config_path: Annotated[Optional[Path], typer.Option()] = None,
    artefact_path: Annotated[Optional[Path], typer.Option()] = None,
):
    config_is_valid = parse_project(config_path, artefact_path)
    if config_is_valid:
        print("Config is valid ✅")


@app.command()
def validate(config_path: Annotated[Optional[Path], typer.Option()] = None): ...
