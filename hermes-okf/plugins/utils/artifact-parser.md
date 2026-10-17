---
type: Plugin
title: Artifact Parser
description: Utility for parsing and validating Hermes pipeline artifact definition files
resource: plugins/utils/hermes_artifact_parser/
tags: [plugin, utility, parser, artifacts, validation]
status: stable
generated: { by: "pi/claude-sonnet-4-20250514", at: "2025-07-17T00:00:00Z" }
---

# Artifact Parser

Utility plugin for parsing Hermes artifact files (`definitions.json`). These files contain the merged configuration of all sources, destinations, and pipelines for a Hermes project.

## Purpose

The artifact parser consolidates individual YAML configuration files from the configuration folder into a single `definitions.json` that the pipeline engine consumes at runtime. It is used by the [CLI](/plugins/utils/hermes-cli.md) during project initialization and validation.

## Entry Point

```toml
[project.entry-points."hermes_plugins.utils"]
hermes_artifact_parser = "hermes_artifact_parser:..."
```
