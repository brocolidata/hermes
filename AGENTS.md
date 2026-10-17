# AGENTS.md

## Knowledge Bundle

This project includes an **OKF (Open Knowledge Format) v0.2 knowledge bundle** at `hermes-okf/`. Before diving into the source code, read the bundle for structured context:

1. Start with [`hermes-okf/index.md`](hermes-okf/index.md) for a full concept map of the codebase
2. Read [`hermes-okf/architecture.md`](hermes-okf/architecture.md) for high-level design, data flow, and key design decisions
3. Browse subdirectory indexes (`core/index.md`, `plugins/index.md`, etc.) to locate specific concepts
4. Each concept file contains frontmatter metadata and detailed documentation of the module it describes

The bundle is the **preferred source of architectural context** — use it to understand module responsibilities, class relationships, plugin conventions, and configuration patterns before reading raw source files.

## Project Overview

Hermes is a lightweight, serverless-compatible Python **Extract-Load (EL)** framework with a plugin-based architecture. It lets users define data pipelines in YAML that extract from configurable sources and load into configurable destinations.

- **Version:** 0.4.1 (alpha)
- **Python:** 3.12 only (`>=3.12,<3.13`)
- **Package manager:** [uv](https://docs.astral.sh/uv/)
- **Build system:** Hatchling

## Repository Layout

```
hermes/                     # Core library package
  main.py                   # Entry point: run_pipeline(name)
  pipeline.py               # Pipeline (config) + PipelineRun (execution) classes
  connectors.py             # Entry-point-based plugin loader
  settings.py               # Path resolution, env vars, constants, enums
  exceptions.py             # Error hierarchy (HermesError → Source/Destination/Pipeline/ConfigLoad)
  utils.py                  # Definition file loading via OmegaConf
  logging_utils.py          # Logger factory
  sources/utils.py          # BaseSource ABC
  destinations/utils.py     # BaseDestination ABC

plugins/                    # Each plugin is an independent Python package
  sources/
    custom/                 # CustomSource — user-defined Python extractors
  destinations/
    athena_iceberg/         # AWS Athena Iceberg tables via awswrangler
    generic_object_storage/ # Abstract fsspec-based object storage base
    s3/                     # AWS S3 (extends generic_object_storage)
    local_storage/          # Local filesystem (extends generic_object_storage)
  utils/
    hermes_cli/             # Typer CLI for project scaffolding & pipeline execution
    hermes_artifact_parser/ # definitions.json parser & validator

tests/
  conftest.py               # Shared fixtures (AWS env, mock sources, config helpers)
  unit_tests/               # Per-module unit tests
  integration_tests/        # End-to-end source/destination tests
  plugins/utils/            # Plugin-specific tests
  assets/                   # Test fixtures: sample configs, data, project structure
```

## Setup

```bash
uv venv
uv sync --all-extras --all-groups
```

This installs all plugins as editable dependencies (configured in `pyproject.toml` under `[tool.uv.sources]`).

## Key Architecture Concepts

- **Pipeline vs PipelineRun** — `Pipeline` is the static config; `PipelineRun` holds execution state (successes/errors list). Created via `Pipeline.create_run()`.
- **Plugin discovery** — Connectors are loaded at runtime via `importlib.metadata.entry_points`. Sources register under `hermes_plugins.sources`, destinations under `hermes_plugins.destinations`.
- **Configuration** — Pipelines are defined in YAML, merged into `definitions.json`, and loaded via OmegaConf. Project paths resolve from env vars (`HERMES_PROJECT_PATH`, `HERMES_CONFIG_FOLDER`, `HERMES_ARTIFACTS_FOLDER`, `HERMES_CUSTOM_CONNECTORS_FOLDER`) or from `hermes_config.yml`.
- **Cartesian execution** — A pipeline run iterates over `(sources × destinations) × tables`. Errors are collected per-step; the run does not abort on failure.
- **Data stages** — Destinations declare `data_stage = "raw"` (dict) or `"processed"` (DataFrame). The pipeline routes data accordingly.

## Plugin Conventions

Each plugin lives in `plugins/{sources,destinations,utils}/<name>/` and has:

- Its own `pyproject.toml` with `[project.entry-points."hermes_plugins.<type>"]`
- A connector module with a class extending `BaseSource` or `BaseDestination`
- An `__init__.py` that re-exports the connector class
- Optional `exceptions.py` for plugin-specific errors

When creating a new plugin:
1. Create the package directory under the appropriate `plugins/` subfolder
2. Implement the connector class extending `BaseSource` or `BaseDestination`
3. Register the entry point in `pyproject.toml`
4. Add the editable source in the root `pyproject.toml` under `[tool.uv.sources]` and `[project.optional-dependencies]`
5. Run `uv sync --all-extras --all-groups` to install

## Testing

```bash
# Run all tests
uv run pytest

# Run unit tests only
uv run pytest tests/unit_tests/

# Run integration tests only
uv run pytest tests/integration_tests/
```

- Tests use **pytest** with fixtures defined in `tests/conftest.py`
- AWS services are mocked with **moto** (`moto>=5.1.1`)
- Test assets (sample configs, data files, project structures) live in `tests/assets/`
- Fixtures provide: AWS env var setup, fsspec mocking, Athena mocking, sample configs, custom source mocking

## Code Style & Patterns

- **Type hints** — Use throughout; the package ships a `py.typed` marker
- **Error handling** — All custom exceptions inherit from `HermesError` and auto-log on creation. Use `SourceError`, `DestinationError`, `PipelineError`, or `ConfigLoadError` as appropriate
- **Configuration** — Always use OmegaConf `DictConfig` for config objects, never raw dicts
- **Logging** — Import via `from hermes.logging_utils import get_logger`; use the returned root logger
- **Path resolution** — Use `hermes.settings` functions; never hardcode paths
- **Match statements** — Used for connector type routing and data stage branching (Python 3.12)

## Important Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Root package config, all plugin source mappings, optional dependency groups |
| `hermes/__init__.py` | Public API: re-exports `run_pipeline` and `get_pipeline` |
| `hermes/pipeline.py` | Core orchestration logic — most changes to pipeline behavior go here |
| `hermes/connectors.py` | Plugin loading — modify only if changing discovery mechanism |
| `hermes/settings.py` | All path resolution and constants — modify when adding new config options |
| `tests/conftest.py` | Shared test fixtures — update when adding new test infrastructure |
