import logging  # Import the logging module
import os
import platform
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path
from typing import Optional

import questionary
import typer
from cli.main import (
    get_hermes_connectors,
    parse_project,
)
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated

from hermes import utils
from hermes.pipeline import get_pipeline

app = typer.Typer()

pipeline_app = typer.Typer()
console = Console()

app.add_typer(pipeline_app, name="pipeline")


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
def install_connector():
    """Install a connector"""
    connectors = get_hermes_connectors()

    if not connectors:
        typer.echo("No local connectors found")
        raise typer.Exit(code=1)

    selected_connectors = questionary.checkbox(
        "Select a specific Connector(s) to install:",
        choices=connectors,
        validate=lambda x: True if x else "Please select at least one item!",
    ).ask()

    # Handle user cancellation
    if selected_connectors is None:
        typer.echo("Installation cancelled")
        raise typer.Exit(code=0)

    if not selected_connectors:
        typer.echo("No connectors selected")
        raise typer.Exit(code=1)

    # Format connectors for installation
    connectors_str = ",".join(selected_connectors)
    typer.echo(f"Selected connectors: {connectors_str}")

    # Build installation URL
    connectors_install_url = f'uv pip install "git+https://github.com/brocolidata/hermes#subdirectory=src["{connectors_str}"]"'
    typer.echo(f"Command: {connectors_install_url}")
    typer.echo("Installing connectors...")

    try:
        result = subprocess.run(
            connectors_install_url,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
        )

        typer.echo(f"✅ Successfully installed connectors: {connectors_str}")
        if result.stdout:
            typer.echo(f"Output: {result.stdout}")

    except subprocess.CalledProcessError as e:
        typer.echo(f"❌ Error installing connectors: {e}")
        if e.stderr:
            typer.echo(f"Error details: {e.stderr}")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"❌ Unexpected error: {str(e)}")
        raise typer.Exit(code=1)


@app.command()
def debug(
    logging_level: Annotated[
        Optional[str],
        typer.Option(
            help="Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL).",
            rich_help_panel="Logging Options",
        ),
    ] = "INFO",
):
    """Show information on the current Hermes environment and check installed connectors"""

    setup_logging(logging_level)

    print("\n[SYSTEM INFORMATION]")
    print(f"• Hermes Version : {version('hermes')}")
    print(f"• Python Version: {sys.version.split()[0]}")
    print(f"• Python Path   : {sys.executable}")
    print(f"• Platform      : {platform.system()} {platform.release()}")
    print(f"• Working Dir   : {os.getcwd()}")

    supported = get_hermes_connectors()

    if supported:
        print("\n[SUPPORTED CONNECTORS]")
        for connector in supported:
            print(f"  - {connector}")
    else:
        print("No connectors installed.")


@app.command()
def setup_project():
    """Set up a Hermes project with required environment variables."""
    typer.echo("Setting up Hermes project...")


@pipeline_app.command("run")
def run_pipeline(name: str):
    """Run Pipeline"""
    definitions = utils.get_definitions_from_file()
    available_pipelines = [pipeline.name for pipeline in definitions.pipelines]
    if name in available_pipelines:
        try:
            pipeline = get_pipeline(name)
            print(f"Running pipeline: {name}")
            pipeline.run()
            print(f"Pipeline {name} completed successfully.")

        except Exception as e:
            print(f"Error running pipeline {name}: {e}")
            raise typer.Exit(code=1)
    else:
        print(f"Pipeline {name} not found in available pipelines.")
        raise typer.Exit(code=1)


@pipeline_app.command("list")
def list_pipelines():
    """List available pipelines"""
    definitions = utils.get_definitions_from_file()
    pipelines = definitions.pipelines

    if not pipelines:
        console.print("[bold red]No pipelines found.[/bold red]")
        raise typer.Exit(code=1)

    table = Table(title="Available Pipelines")
    table.add_column("Pipeline Name", style="cyan", no_wrap=True)
    table.add_column("Sources", style="green")
    table.add_column("Destinations", style="magenta")

    for pipeline in pipelines:
        sources_list = [src["name"] for src in pipeline["sources"]]
        destinations_list = pipeline["destinations"]

        table.add_row(
            pipeline["name"], ", ".join(sources_list), ", ".join(destinations_list)
        )

    console.print(table)
    raise typer.Exit(code=0)


@app.command()
def artefact_parse(
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
def artefact_validate(
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
