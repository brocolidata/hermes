import os
from typing import Optional

import questionary
import typer
from cli.main import get_connectors

# import subprocess
app = typer.Typer()


@app.command()
def install_connector():
    """Install a connector"""
    connectors = get_connectors()

    if not connectors:
        typer.echo("No local connectors found ")
    else:
        selected_connectors = questionary.checkbox(
            "Select a specific Connector(s) to install:",
            choices=connectors,
            validate=lambda x: True if x else "Please select at least one item!",
        ).ask()
    typer.echo(f"Selected connectors: {selected_connectors}")
    for connector in selected_connectors:
        connector_url = f'uv pip install "git+https://github.com/brocolidata/hermes#subdirectory=src["{connector}"]"'
        os.system(connector_url)
        # subprocess.run(connector_url, shell=True, check=True)

        typer.echo(f"Installing connector from {connector_url}...")
        try:
            # uv.pip.install([connector_url], editable=False)
            typer.echo(f"Successfully installed connector from {connector_url}")
        except Exception as e:
            typer.echo(f"Error installing connector from {connector_url}: {str(e)}")
            raise typer.Exit(code=1)


@app.command()
def setup_project():
    """Set up a Hermes project with required environment variables."""
    typer.echo("Setting up Hermes project...")


@app.command()
def run_pipelines(pipeline_name: Optional[str] = None):
    """Run all pipelines or a specific pipeline."""
    typer.echo(
        f"Running pipelines{' for ' + pipeline_name if pipeline_name else ''}..."
    )
