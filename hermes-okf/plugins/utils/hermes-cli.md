---
type: Plugin
title: Hermes CLI
description: Typer-based command-line interface for project scaffolding, inspection, and pipeline execution
resource: plugins/utils/hermes_cli/cli/cli.py
tags: [plugin, cli, typer, developer-tools]
status: stable
generated: { by: "pi/claude-sonnet-4-20250514", at: "2025-07-17T00:00:00Z" }
---

# Hermes CLI

A [Typer](https://typer.tiangolo.com/)-based CLI for managing Hermes projects. Uses [Rich](https://rich.readthedocs.io/) for console output.

## Entry Point

```toml
[project.scripts]
hermes = "cli.cli:app"
```

## Commands

### Top-Level

| Command         | Description                                                  |
|-----------------|--------------------------------------------------------------|
| `hermes info`   | Display system information, Hermes version, and installed connectors |
| `hermes init`   | Interactive project scaffolding wizard                       |

### Pipeline Subcommands (`hermes pipeline ...`)

| Command                        | Description                                     |
|--------------------------------|-------------------------------------------------|
| `hermes pipeline run <name>`   | Execute a named pipeline                        |
| `hermes pipeline list`         | List all configured pipelines                   |

## Project Scaffolding (`hermes init`)

The `init` command interactively:

1. Asks for project root directory
2. Creates folder structure (`artifacts/`, `configuration/`, `custom_connectors/`)
3. Generates `hermes_config.yml` with resolved paths
4. Lists available source/destination connectors for selection
5. Generates a starter `definitions.json` and pipeline YAML

## Helper Module: `cli/main.py`

| Function                           | Description                                              |
|------------------------------------|----------------------------------------------------------|
| `get_installed_hermes_connectors()`| Queries entry points to list all installed plugins       |
| `get_available_connectors()`       | Returns connectors available for project configuration   |
| `parse_project()`                  | Parses and validates the current Hermes project          |

### JSON Schema Validation

The CLI uses a JSON schema (`cli/json_schemas/json_schema.json`) to validate `definitions.json` files during project parsing.

## Dependencies

- `typer` — CLI framework
- `rich` — Console formatting
- `questionary` — Interactive prompts
- `jsonschema` — Definition file validation
