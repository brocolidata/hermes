---
type: Plugin
title: Athena Iceberg Destination
description: AWS Athena Iceberg table destination using AWS Data Wrangler
resource: plugins/destinations/athena_iceberg/athena_iceberg_destination/connector.py
tags: [plugin, destination, athena, iceberg, aws, data-lake]
status: stable
generated: { by: "pi/claude-sonnet-4-20250514", at: "2025-07-17T00:00:00Z" }
---

# Athena Iceberg Destination

Loads processed DataFrames into AWS Athena Iceberg tables using `awswrangler`.

## Entry Point

```toml
[project.entry-points."hermes_plugins.destinations"]
athena_iceberg = "athena_iceberg_destination:AthenaIcebergDestination"
```

**Type in YAML config:** `athena_iceberg`

## Class: `AthenaIcebergDestination`

Extends [BaseDestination](/core/connectors.md).

**`data_stage`:** `"processed"` — receives Pandas DataFrames (post-processing by the source connector).

### Configuration

| Key              | Description                                  | Required |
|------------------|----------------------------------------------|----------|
| `glue_database`  | AWS Glue database name                       | yes      |
| `table_location` | S3 base path for Iceberg table storage       | yes      |
| `temp_path`      | S3 temp path for Athena write operations     | yes      |
| `workgroup`      | Athena workgroup (default: `"primary"`)      | no       |

### Key Methods

| Method                                              | Description                                            |
|-----------------------------------------------------|--------------------------------------------------------|
| `load(source_name, table_name, data: DataFrame)`    | Creates/appends to an Iceberg table via `wr.athena.to_iceberg()` |
| `_get_full_table_location(source, table)`           | `{table_location}/{source}/{table}/`                   |
| `_get_full_temp_path(source, table)`                | `{temp_path}/{source}/{table}/`                        |

### Write Behavior

Uses `awswrangler.athena.to_iceberg()` with:
- `table_type = "ICEBERG"`
- `mode = "append"`
- `keep_files = False`
- `schema_evolution = True`

### Dependencies

- `awswrangler` (AWS SDK for Pandas)
- `pandas`

## Exceptions

`AthenaIcebergDestinationError` wraps `DestinationError` with Athena-specific context.
