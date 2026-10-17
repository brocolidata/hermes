---
type: Python Module
title: Logging Utils
description: Centralized logger factory for Hermes
resource: hermes/logging_utils.py
tags: [core, logging]
status: stable
generated: { by: "pi/claude-sonnet-4-20250514", at: "2025-07-17T00:00:00Z" }
---

# Logging Utils

Provides a single function `get_logger()` that returns the Python root logger. All Hermes modules use this to obtain a consistent logger instance.

## Function

### `get_logger() → logging.RootLogger`

Returns `logging.getLogger()` — the root logger. The [CLI](/plugins/utils/hermes-cli.md) configures the root logger's level and handlers at startup via `setup_logging()`.
