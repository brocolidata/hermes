---
type: Plugin
title: Generic Object Storage Destination
description: Abstract base destination for object storage services (S3, GCS, local filesystem)
resource: plugins/destinations/generic_object_storage/generic_object_storage_destination/connector.py
tags: [plugin, destination, object-storage, abstract]
status: stable
generated: { by: "pi/claude-sonnet-4-20250514", at: "2025-07-17T00:00:00Z" }
---

# Generic Object Storage Destination

Abstract base class for all object-storage-style destinations. Provides common logic for path construction and JSON-based loading via `fsspec`.

## Class: `ObjectStorageDestination`

Extends [BaseDestination](/core/connectors.md). Subclassed by [S3](/plugins/destinations/s3.md) and [Local Storage](/plugins/destinations/local-storage.md).

**`data_stage`:** `"raw"` — receives raw dict data, not DataFrames.

### Configuration

| Key      | Description                           | Required |
|----------|---------------------------------------|----------|
| `format` | Output file format (e.g. `json`)      | yes      |
| `bucket` | Destination bucket or folder name     | yes      |

### Abstract Property

| Property | Description                                           |
|----------|-------------------------------------------------------|
| `prefix` | Storage protocol prefix (e.g. `s3:/` or empty string) |

### Key Methods

| Method                                        | Description                                              |
|-----------------------------------------------|----------------------------------------------------------|
| `get_object_path(source_name, table_name)`    | Builds full path: `{prefix}/{bucket}/{source}/{table}/{table}_{timestamp}.{format}` |
| `load(source_name, table_name, data)`         | Writes JSON data to the resolved path using `fsspec`     |

### Path Format

```
{prefix}/{bucket}/{source_name}/{table_name}/{table_name}_{MM_DD_YYYY_HH_MM_SS}.{format}
```

## Exceptions

`ObjectStorageDestinationError` wraps `DestinationError` with the file path and underlying error.
