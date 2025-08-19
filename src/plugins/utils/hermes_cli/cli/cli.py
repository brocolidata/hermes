import logging  # Import the logging module
import os
import platform
import subprocess
import sys
import tomllib
from importlib.metadata import version
from pathlib import Path
from typing import Optional

import questionary
import typer
from cli.main import (
    get_installed_hermes_connectors,
    parse_project,
)
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from typing_extensions import Annotated

from hermes import utils
from hermes.pipeline import get_pipeline
from hermes.settings import get_config_file_path

app = typer.Typer(
    name="hermes",
    help="Hermes Command Line Interface",
    add_completion=False,
    rich_markup_mode="rich",
)

pipeline_app = typer.Typer(
    name="pipeline",
    help="Pipeline management commands - list and run your data pipelines",
    rich_markup_mode="rich",
)
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


def find_pyproject_toml() -> str:
    """Locate pyproject.toml by traversing up from the current working directory."""
    current_dir = os.getcwd()
    while current_dir != os.path.dirname(current_dir):  # Stop at root
        pyproject_path = os.path.join(current_dir, "pyproject.toml")
        if os.path.isfile(pyproject_path):
            return pyproject_path
        current_dir = os.path.dirname(current_dir)
    raise FileNotFoundError("pyproject.toml not found")


def get_available_connectors():
    """Extract connectors ending with 'source' or 'destination' from tool.uv.sources."""
    pyproject_path = find_pyproject_toml()
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
    sources = data.get("tool", {}).get("uv", {}).get("sources", {})
    hermes_connectors = [
        key for key in sources if key.endswith(("_source", "_destination"))
    ]
    # Exclude connectors that ends with '_source' or '_destination'
    excluded_connectors = ["generic_object_storage_destination"]
    connectors = [
        connector
        for connector in hermes_connectors
        if connector not in excluded_connectors
    ]
    return connectors


def get_hermes_version(value: bool):
    """Show version information and exit"""
    if value:
        console.print(
            f"[bold blue]Hermes[/bold blue] version : [green]{version('hermes')}[/green]"
        )
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-v",
            callback=get_hermes_version,
            is_eager=True,
            help="Show Hermes version",
        ),
    ] = None,
):
    """
    Hermes Command Line Interface
    """
    return


@app.command(name="install")
def install_connector():
    """
    Install Hermes connectors

    Select and install connectors for various data sources and destinations.
    """

    with console.status("[bold green]🔍 Scanning for available connectors..."):
        connectors = get_available_connectors()
        # sources = [
        #     f"{source_connector}_source"
        #     for source_connector in hermes_connectors["sources"]
        # ]
        # destinations = [
        #     f"{destination_connector}_destination"
        #     for destination_connector in hermes_connectors["destinations"]
        # ]
        # connectors = sources + destinations
    if not connectors:
        console.print("[bold red]❌ No local connectors found[/bold red]")
        raise typer.Exit(code=1)

    console.print(
        f"\n✅ Found [bold green]{len(connectors)}[/bold green] available connectors"
    )

    selected_connectors = questionary.checkbox(
        "🎯 Select connectors to install:",
        choices=connectors,
        validate=lambda x: True if x else "❌ Please select at least one connector!",
        style=questionary.Style(
            [
                ("question", "bold"),
                ("answer", "fg:#ff9d00 bold"),
                ("pointer", "fg:#ff9d00 bold"),
                ("highlighted", "fg:#ff9d00 bold"),
                ("selected", "fg:#cc5454"),
                ("separator", "fg:#cc5454"),
                ("instruction", ""),
                ("text", ""),
                ("disabled", "fg:#858585 italic"),
            ]
        ),
    ).ask()

    # Handle user cancellation
    if selected_connectors is None:
        console.print("\n[yellow]🚫 Installation cancelled by user[/yellow]")
        raise typer.Exit(code=0)

    if not selected_connectors:
        console.print("[bold red]❌ No connectors selected[/bold red]")
        raise typer.Exit(code=1)

    # Format connectors for installation
    connectors_str = ",".join(selected_connectors)
    typer.echo(f"Selected connectors: {connectors_str}")

    # Build installation URL
    connectors_install_url = f'uv pip install "git+https://github.com/brocolidata/hermes#subdirectory=src["{connectors_str}"]"'
    typer.echo(f"Command: {connectors_install_url}")
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Installing connectors...", total=None)

        result = subprocess.run(
            connectors_install_url,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
        )

        console.print(
            f"\n✅ [bold green]Successfully installed connectors:[/bold green] {connectors_str}"
        )
        if result.stdout:
            console.print(
                Panel(result.stdout, title="📄 Installation Output", style="dim")
            )

    except subprocess.CalledProcessError as e:
        console.print(f"\n❌ [bold red]Error installing connectors:[/bold red] {e}")
        if e.stderr:
            console.print(Panel(e.stderr, title="🚨 Error Details", style="red"))
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"\n❌ [bold red]Unexpected error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


@app.command(name="debug")
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

    installed_connectors = get_installed_hermes_connectors()

    if installed_connectors:
        print("\n[INSTALLED CONNECTORS]")
        print("Sources:")
        for source in installed_connectors["sources"]:
            print(f"  - {source}")
        print("Destinations:")
        for destination in installed_connectors["destinations"]:
            print(f"  - {destination}")
    else:
        print("No connectors installed.")

    config_file_path = get_config_file_path()
    print("\n[CONFIGURATION FILE]")
    if config_file_path:
        print(
            f"[bold green]• config.yml file Found[/bold green] in : {config_file_path}"
        )
    else:
        print("[bold red]No configuration file found.[/bold red]")


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


@app.command(name="init")
def init_command():
    from hermes.settings import generate_config_file

    """Initialize the Hermes CLI command"""
    try:
        generate_config_file()
    except Exception as e:
        console.print(f"[bold red]Error generating configuration file:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command(name="test")
def test_get_config_file():
    from hermes.settings import get_artifacts_folder, get_config_folder

    """Test the get_config_file function"""
    try:
        config_folder = get_config_folder()
        artefact_folder = get_artifacts_folder()
        console.print(f"[bold green]Configuration folder:[/bold green] {config_folder}")
        console.print(f"[bold green]Artifacts folder:[/bold green] {artefact_folder}")
    except Exception as e:
        console.print(f"[bold red]Error getting configuration folder:[/bold red] {e}")
        raise typer.Exit(code=1)
