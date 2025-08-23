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
from hermes.settings import (
    HERMES_CONFIG_FILE,
    get_artifacts_folder,
    get_config_folder,
    get_custom_connectors_folder,
    get_hermes_config_file_path,
)


class FileStorage:
    def __init__(self, root_path: str):
        self.root = Path(root_path).resolve()

    def make_full_path(self, rel_path: str) -> str:
        return str(self.root / rel_path)

    def has_folder(self, rel_path: str) -> bool:
        return (self.root / rel_path).is_dir()

    def create_folder(self, rel_path: str):
        (self.root / rel_path).mkdir(parents=True, exist_ok=True)

    def has_file(self, rel_path: str) -> bool:
        return (self.root / rel_path).is_file()

    def save(self, rel_path: str, content: str):
        full_path = self.root / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)


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


def get_available_connectors():
    """Extract connectors ending with '_source' or '_destination' from tool.uv.sources."""
    return [
        "custom_source",
        "athena_iceberg_destination",
        "s3_destination",
        "local_storage_destination",
    ]


def get_hermes_version(value: bool):
    """Show version information and exit"""
    if value:
        console.print(
            f"[bold blue]Hermes[/bold blue] version : [green]{version('hermes')}[/green]"
        )
        raise typer.Exit()


def debug_hermes_system_info():
    """Print Hermes system information"""
    print("\n[SYSTEM INFORMATION]")
    print(f"• Hermes Version  : {version('hermes')}")
    print(f"• Python Version  : {sys.version.split()[0]}")
    print(f"• Python Path     : {sys.executable}")
    print(f"• Platform        : {platform.system()} {platform.release()}")
    print(f"• Working Dir     : {os.getcwd()}")


def debug_hermes_connectors():
    """Print Hermes connectors information"""
    print("\n[HERMES CONNECTORS]")
    try:
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
    except Exception as e:
        print(f"[bold red]Error retrieving connectors:[/bold red] {e}")


def debug_hermes_configurations():
    """Show Hermes configuration informations"""
    config_file_path = get_hermes_config_file_path()
    print("\n[HERMES CONFIGURATION FILE]")
    if config_file_path:
        print(
            f"[bold green]• {HERMES_CONFIG_FILE} file Found[/bold green] at : {config_file_path}"
        )
    else:
        print(f"[bold red]No {HERMES_CONFIG_FILE} configuration file found.[/bold red]")

    print("\n[HERMES CONFIGURATION VARIABLES]")

    # Check HERMES_CONFIG_FOLDER
    try:
        config_dict = get_config_folder()
        print(
            f"[bold green]• HERMES_CONFIG_FOLDER Found[/bold green] at : {config_dict['path']} | Using {'Environment variable ' if config_dict['source'] == 'environment_variable' else 'Configuration file'}"
        )
    except Exception as e:
        print(f"[bold red]• HERMES_CONFIG_FOLDER Error:[/bold red] {e}")

    # Check HERMES_CUSTOM_CONNECTORS_FOLDER
    try:
        custom_dict = get_custom_connectors_folder()
        print(
            f"[bold green]• HERMES_CUSTOM_CONNECTORS_FOLDER Found[/bold green] at : {custom_dict['path']} | Using {'Environment variable ' if custom_dict['source'] == 'environment_variable' else 'Configuration file'}"
        )
    except Exception as e:
        print(f"[bold red]• HERMES_CUSTOM_CONNECTORS_FOLDER Error:[/bold red] {e}")

    # Check HERMES_ARTIFACTS_FOLDER
    try:
        artefact_dict = get_artifacts_folder()
        print(
            f"[bold green]• HERMES_ARTIFACTS_FOLDER Found[/bold green] at : {artefact_dict['path']} |  Using {'Environment variable ' if artefact_dict['source'] == 'environment_variable' else 'Configuration file'}"
        )
    except Exception as e:
        print(f"[bold red]• HERMES_ARTIFACTS_FOLDER Error:[/bold red] {e}")


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
    github_url = "https://github.com/brocolidata/hermes.git@refs/pull/36/head"
    connectors_install_url = (
        f'uv pip install "git+{github_url}#subdirectory=src["{connectors_str}"]"'
    )
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

    debug_hermes_system_info()

    debug_hermes_connectors()

    debug_hermes_configurations()

    raise typer.Exit(code=0)


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
def init_command(destination_path: str = None):
    """Initialize the Hermes CLI command"""
    try:
        destination_path = destination_path or os.getcwd()
        dest_storage = FileStorage(destination_path)
        folders_to_create = ["configuration", "artefacts", "custom_connectors"]
        hermes_content = """# hermes_config.yml - Default configuration
project_paths:
    configuration_folder: ./configuration
    artefacts_folder: ./artefacts
    custom_connectors_folder: ./custom_connectors
"""

        created_items = {}

        # Step 1: Create folders
        for folder in folders_to_create:
            if not dest_storage.has_folder(folder):
                dest_storage.create_folder(folder)
                created_items[folder] = "folder_created"

        # Step 2: Generate hermes_config.yml if it doesn't exist
        hermes_path = dest_storage.make_full_path(HERMES_CONFIG_FILE)
        if dest_storage.has_file(HERMES_CONFIG_FILE):
            console.print(
                f"[bold yellow]Warning:[/bold yellow] {hermes_path} already exists, skipping creation."
            )
        else:
            dest_storage.save(HERMES_CONFIG_FILE, hermes_content)
            created_items[hermes_path] = "generated"

        # Step 3: Welcome message
        console.print(
            f"[bold green] Project initialized in {destination_path}, Folders created: configuration, artefacts, custom_connectors.[/bold green]"
        )

        if hermes_path in created_items:
            console.print(
                f"[bold green]{HERMES_CONFIG_FILE} file created:[/bold green] {hermes_path}"
            )
        else:
            console.print(
                f"[bold yellow]{HERMES_CONFIG_FILE} file already exists:[/bold yellow] {hermes_path}"
            )

        # Ask user if he want to install connector
        confirm_install = typer.confirm(
            "Do you want to install Hermes connectors?",
            default=True,
        )
        if confirm_install:
            console.print("[bold green]Installing Hermes connectors...[/bold green]")
            install_connector()
        else:
            console.print("[bold yellow]Skipping connector installation.[/bold yellow]")

        return created_items

    except Exception as e:
        console.print(f"[bold red]Error generating configuration file:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command(name="test")
def test_get_config_file():
    """Test the get_config_file function"""
    config_folder = get_config_folder()
    artefact_folder = get_artifacts_folder()
    custom_connectors_folder = get_custom_connectors_folder()
    console.print(
        f"[bold green]Configuration folder:[/bold green] {config_folder['path']} Using {config_folder['source']}"
    )
    console.print(
        f"[bold green]Artifacts folder:[/bold green] {artefact_folder['path']} Using {artefact_folder['source']}"
    )
    console.print(
        f"[bold green]Custom connectors folder:[/bold green] {custom_connectors_folder['path']} Using {custom_connectors_folder['source']}"
    )
