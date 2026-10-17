---
type: Python Module
title: Settings
description: Project configuration, path resolution, environment variables, and constants
resource: hermes/settings.py
tags: [core, configuration, environment, paths]
status: stable
generated: { by: "pi/claude-sonnet-4-20250514", at: "2025-07-17T00:00:00Z" }
---

# Settings

Centralizes project path resolution, constants, and enumerations used throughout Hermes.

## Constants

| Constant                  | Value                | Description                    |
|---------------------------|----------------------|--------------------------------|
| `HERMES_DEFINITIONS_FILE` | `"definitions.json"` | Name of the definitions file   |
| `HERMES_CONFIG_FILE`      | `"hermes_config.yml"`| Name of the config file        |

## Enumerations

### `ConnectorsMetaTypes`

```python
class ConnectorsMetaTypes(str, enum.Enum):
    source = "source"
    destination = "destination"
```

### `ObjectStorageServicesPrefixes`

```python
class ObjectStorageServicesPrefixes(str, enum.Enum):
    gcs = "gs:/"
    s3 = "s3:/"
```

### `NodeTypes`

```python
class NodeTypes(str, enum.Enum):
    sources = "sources"
    destinations = "destinations"
    pipelines = "pipelines"
```

## Path Resolution

All folder paths are resolved via a two-tier strategy:

1. **Environment variable** (highest priority)
2. **`hermes_config.yml`** file fallback

### Key Functions

| Function                              | Returns              | Description                                        |
|---------------------------------------|----------------------|----------------------------------------------------|
| `get_hermes_project_folder_from_env_var()` | `str \| None`   | Reads `HERMES_PROJECT_PATH` env var                |
| `load_hermes_config_file()`           | `dict`               | Loads and parses `hermes_config.yml`               |
| `get_config_folder()`                 | `dict`               | Resolves configuration folder path                 |
| `get_artifacts_folder()`              | `dict`               | Resolves artifacts folder path                     |
| `get_custom_connectors_folder()`      | `dict`               | Resolves custom connectors folder path             |
| `get_definition_file_path()`          | `Path`               | Full path to `definitions.json`                    |
| `get_hermes_config_file_path()`       | `Path`               | Full path to `hermes_config.yml`                   |

### `resolve_path_from_env_config(env_var_name, config_key, path_description, create_if_missing=False) → dict`

Generic helper that resolves a path from an environment variable or config file. Returns `{"path": Path, "source": "environment_variable" | "configuration_file"}`. Supports relative-to-project-root resolution and optional directory creation.
