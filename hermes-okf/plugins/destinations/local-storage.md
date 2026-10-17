---
type: Plugin
title: Local Storage Destination
description: Local filesystem destination connector for development and testing
resource: plugins/destinations/local_storage/local_storage_destination/connector.py
tags: [plugin, destination, local, filesystem]
status: stable
generated: { by: "pi/claude-sonnet-4-20250514", at: "2025-07-17T00:00:00Z" }
---

# Local Storage Destination

Concrete implementation of [Generic Object Storage](/plugins/destinations/generic-object-storage.md) for the local filesystem.

## Entry Point

```toml
[project.entry-points."hermes_plugins.destinations"]
local_storage = "local_storage_destination:LocalStorageDestination"
```

**Type in YAML config:** `local_storage`

## Class: `LocalStorageDestination`

Extends `ObjectStorageDestination`. Sets `prefix = ""` (empty string) so `fsspec` writes directly to local paths.

The `bucket` config key represents the local folder where data will be written.

### Configuration

| Key      | Description                     | Required |
|----------|---------------------------------|----------|
| `format` | Output file format              | yes      |
| `bucket` | Local folder path for output    | yes      |
