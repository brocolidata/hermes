import logging  # Import the logging module
from pathlib import Path
from typing import Optional

import typer
from artefact_parser.main import parse_project
from typing_extensions import Annotated

app = typer.Typer()


def setup_logging(level_str: str):
    """
    Configures the root logger and its handlers based on the provided level string.
    """
    try:
        level = getattr(logging, level_str.upper())
    except AttributeError:
        level = logging.INFO
        print(f"Warning: Invalid logging level '{level_str}'. Defaulting to INFO.")

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    handler.setLevel(level)
    root_logger.addHandler(handler)


@app.command()
def parse(
    config_path: Annotated[
        Optional[Path],
        typer.Option(
            help="Path to the configuration folder (defined by `HERMES_CONFIG_FOLDER` env var ).",
            rich_help_panel="Input/Output Options",
        ),
    ] = None,
    artefact_path: Annotated[
        Optional[Path],
        typer.Option(
            help="Path to the folder where the definitions.json will be written (defined by `HERMES_ARTIFACTS_FOLDER` env var).",
            rich_help_panel="Input/Output Options",
        ),
    ] = None,
    logging_level: Annotated[
        Optional[str],
        typer.Option(
            help="Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL).",
            rich_help_panel="Logging Options",
        ),
    ] = "INFO",  # Default logging level is INFO
):
    """
    Parses, validates, and merges YAML configuration files into a single JSON definition file.
    """
    setup_logging(logging_level)

    _ = parse_project(config_path, artefact_path)


@app.command()
def validate(
    config_path: Annotated[
        Optional[Path],
        typer.Option(
            help="Path to the configuration folder to validate.",
            rich_help_panel="Input/Output Options",
        ),
    ] = None,
    logging_level: Annotated[  # Added logging_level to validate command as well
        Optional[str],
        typer.Option(
            help="Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL).",
            rich_help_panel="Logging Options",
        ),
    ] = "INFO",
):
    """
    Validates YAML configuration files without merging or writing output.
    """
    # Configure logging for the validate command as well
    setup_logging(logging_level)
