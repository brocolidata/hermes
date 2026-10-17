---
type: Plugin
title: Custom Source
description: Source connector that extracts data using user-defined Python extractor functions
resource: plugins/sources/custom/custom_source/connector.py
tags: [plugin, source, custom, extraction]
status: stable
generated: { by: "pi/claude-sonnet-4-20250514", at: "2025-07-17T00:00:00Z" }
---

# Custom Source

The Custom Source plugin allows users to write their own Python extractor classes and reference them in pipeline configuration. It is the only source connector currently shipped with Hermes.

## Entry Point

```toml
[project.entry-points."hermes_plugins.sources"]
custom = "custom_source:CustomSource"
```

**Type in YAML config:** `custom`

## Configuration

| Key           | Description                                            | Required |
|---------------|--------------------------------------------------------|----------|
| `extractor`   | Name of the extractor class/function in the module     | yes      |
| `module_path` | Relative path to the Python module (within custom connectors folder) | yes |
| `tables`      | List of table definitions to extract                   | yes      |

### Table Definition

| Key        | Description                                         | Required |
|------------|-----------------------------------------------------|----------|
| `name`     | Table name used downstream                          | yes      |
| `data_key` | Key in the extracted data dict for this table       | yes      |
| `kwargs`   | Keyword arguments passed to the extractor           | yes      |

## Class: `CustomSource`

Extends [BaseSource](/core/connectors.md).

### Initialization

1. Reads `module_path` from config
2. Resolves the module relative to the custom connectors folder (from [Settings](/core/settings.md))
3. Loads the extractor via `runpy.run_path()`
4. Raises `CustomSourceError` if the module or extractor cannot be found

### Key Methods

| Method                          | Description                                                    |
|---------------------------------|----------------------------------------------------------------|
| `extract(table_name, context)` | Calls the extractor with table kwargs + run context            |
| `process_data(raw_data)`        | Converts raw extraction output into a Pandas DataFrame         |
| `_get_table_config(table_name)` | Looks up table configuration by name                          |

### Data Processing

The `process_data` method converts raw dict data into a `pd.DataFrame`. Destinations with `data_stage = "processed"` receive DataFrames; those with `data_stage = "raw"` receive the raw dict keyed by `data_key`.

## Exceptions

`CustomSourceError` wraps `SourceError` with pipeline name and process step context.
