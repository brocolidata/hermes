---
type: Python Module
title: Pipeline Engine
description: Core pipeline orchestration with separate static configuration and execution runtime
resource: hermes/pipeline.py
tags: [core, pipeline, orchestration, scheduling]
status: stable
generated: { by: "pi/claude-sonnet-4-20250514", at: "2025-07-17T00:00:00Z" }
---

# Pipeline Engine

The pipeline module is the heart of Hermes. It provides two classes that separate **configuration** from **execution**.

## Classes

### `Pipeline`

Represents a static data pipeline configuration. Constructed from an OmegaConf `DictConfig` loaded from `definitions.json`.

| Attribute                 | Type                  | Description                                      |
|---------------------------|-----------------------|--------------------------------------------------|
| `pipeline_name`           | `str`                 | Name of the pipeline                             |
| `schedule`                | `str`                 | Cron expression for scheduling                   |
| `sources_tables`          | `dict[str, list]`     | Map of source name → list of table names         |
| `destinations_names`      | `list[str]`           | List of destination connector names              |
| `sources_connectors`      | `list[BaseSource]`    | Loaded source connector instances                |
| `destinations_connectors` | `list[BaseDestination]` | Loaded destination connector instances         |

**Key methods:**

- `create_run(run_context=None) → PipelineRun` — Factory method that computes a cron-based time window and returns a `PipelineRun` instance.

### `PipelineRun`

Manages the lifecycle and state of a single pipeline execution.

| Attribute     | Type         | Description                                 |
|---------------|--------------|---------------------------------------------|
| `pipeline`    | `Pipeline`   | Parent pipeline configuration               |
| `run_context` | `dict`       | Runtime context including time window        |
| `successes`   | `list[dict]` | Records of successful step completions       |
| `errors`      | `list[dict]` | Records of step failures with error details  |

**Key methods:**

- `run() → dict` — Iterates over the Cartesian product of `(sources × destinations)` and executes each table extraction/load step. Returns `{"successes": [...], "errors": [...]}`.
- `_execute_step(table_name, source, destination)` — Handles a single table EL step: extract → process → load.
- `_process_extract(extract, source, table, stage)` — Routes raw vs. processed data based on the destination's `data_stage`.

## Execution Flow

```
Pipeline.create_run()
    → computes cron window via croniter
    → returns PipelineRun

PipelineRun.run()
    → for (source, destination) in product(sources, destinations):
        → for table in source_tables:
            → _execute_step(table, source, destination)
                → source.extract(table, run_context)
                → _process_extract(data, source, table, stage)
                → destination.load(source_name, table, data)
```

## Module-Level Functions

- `get_pipeline(pipeline_name: str) → Pipeline` — Looks up a pipeline by name from `definitions.json`. Raises `PipelineError` if not found.
