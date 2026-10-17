---
type: Python Module
title: Connector Loader
description: Dynamic plugin-based connector loading using Python entry points
resource: hermes/connectors.py
tags: [core, plugins, entry-points, connectors]
status: stable
generated: { by: "pi/claude-sonnet-4-20250514", at: "2025-07-17T00:00:00Z" }
---

# Connector Loader

Dynamically loads source and destination connectors using Python's `importlib.metadata.entry_points` mechanism.

## Function

### `get_connector(dc_connector, connector_meta_type_plural) → BaseSource | BaseDestination`

Loads a connector class from the appropriate entry point group and instantiates it with the given OmegaConf config.

| Parameter                     | Type        | Description                                       |
|-------------------------------|-------------|---------------------------------------------------|
| `dc_connector`                | `DictConfig`| Connector configuration with `type` and `config`  |
| `connector_meta_type_plural`  | `str`       | `"sources"` or `"destinations"`                   |

**Entry point groups:**

| Group                          | Used for             |
|--------------------------------|----------------------|
| `hermes_plugins.sources`       | Source connectors     |
| `hermes_plugins.destinations`  | Destination connectors|

**Error handling:** Raises `ConfigLoadError` if the requested connector type is not found among registered entry points.

## Plugin Registration

Each plugin registers its connector via `[project.entry-points]` in its `pyproject.toml`:

```toml
[project.entry-points."hermes_plugins.sources"]
custom = "custom_source:CustomSource"

[project.entry-points."hermes_plugins.destinations"]
s3 = "s3_destination:S3Destination"
```
