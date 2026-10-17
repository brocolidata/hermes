---
type: Python Module
title: Utils
description: Shared utility for loading pipeline definitions from file
resource: hermes/utils.py
tags: [core, utilities]
status: stable
generated: { by: "pi/claude-sonnet-4-20250514", at: "2025-07-17T00:00:00Z" }
---

# Utils

Minimal utility module providing definition file loading.

## Function

### `get_definitions_from_file() → DictConfig`

Loads the `definitions.json` file (resolved via [Settings](/core/settings.md)) using OmegaConf and returns it as a `DictConfig` object.

This is the primary way the pipeline engine and CLI access the source/destination/pipeline definitions at runtime.
