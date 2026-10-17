---
type: Python Module
title: Exceptions
description: Structured error hierarchy for pipeline, source, destination, and configuration errors
resource: hermes/exceptions.py
tags: [core, errors, exceptions]
status: stable
generated: { by: "pi/claude-sonnet-4-20250514", at: "2025-07-17T00:00:00Z" }
---

# Exceptions

Hermes defines a structured exception hierarchy rooted in `HermesError`. All exceptions automatically log their error message on creation.

## Hierarchy

```
HermesError (base)
├── SourceError          — Data extraction failures
├── DestinationError     — Data loading failures
├── PipelineError        — Pipeline orchestration failures
└── ConfigLoadError      — Configuration loading failures
```

## Classes

### `HermesError`

Base class. Accepts a `message` string, calls `log_error()` on init.

### `SourceError`

| Attribute         | Type  | Description                      |
|-------------------|-------|----------------------------------|
| `connector_name`  | `str` | Name of the source connector     |
| `error_message`   | `str` | Detailed error description       |

Format: `"{connector_name}: {error_message}"`

### `DestinationError`

| Attribute         | Type  | Description                          |
|-------------------|-------|--------------------------------------|
| `connector_name`  | `str` | Name of the destination connector    |
| `error_message`   | `str` | Detailed error description           |

Format: `"{connector_name}: {error_message}"`

### `PipelineError`

| Attribute      | Type  | Description                    |
|----------------|-------|--------------------------------|
| `name`         | `str` | Pipeline name                  |
| `process_step` | `str` | Step where the error occurred  |
| `error`        | `str` | Error details                  |

### `ConfigLoadError`

| Attribute      | Type  | Description                    |
|----------------|-------|--------------------------------|
| `process_step` | `str` | Step where the error occurred  |
| `error`        | `str` | Error details                  |
