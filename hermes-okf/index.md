---
okf_version: "0.2"
---

# Hermes Knowledge Bundle

Hermes is a lightweight, serverless-compatible Python Extract-Load (EL) data framework with a plugin-based architecture. It enables users to define data pipelines that extract from configurable sources and load into configurable destinations using YAML-driven configuration.

**Version:** 0.4.1  
**Language:** Python 3.12  
**Build System:** Hatchling  
**Package Manager:** uv  

## Core

* [Architecture](/architecture.md) — High-level architecture and design patterns
* [Pipeline](/core/pipeline.md) — Pipeline engine: scheduling, orchestration, and execution
* [Connectors](/core/connectors.md) — Plugin-based connector loading via entry points
* [Settings](/core/settings.md) — Project configuration, path resolution, and constants
* [Exceptions](/core/exceptions.md) — Error hierarchy and structured error handling
* [Utils](/core/utils.md) — Shared utility functions
* [Logging](/core/logging.md) — Centralized logging configuration

## Plugins

### Sources
* [Custom Source](/plugins/sources/custom-source.md) — Extract data using user-defined Python functions

### Destinations
* [Generic Object Storage](/plugins/destinations/generic-object-storage.md) — Abstract base for object storage destinations
* [S3 Destination](/plugins/destinations/s3.md) — AWS S3 destination connector
* [Local Storage Destination](/plugins/destinations/local-storage.md) — Local filesystem destination connector
* [Athena Iceberg Destination](/plugins/destinations/athena-iceberg.md) — AWS Athena Iceberg table destination

### Utils
* [Hermes CLI](/plugins/utils/hermes-cli.md) — Command-line interface for project management and pipeline execution
* [Artifact Parser](/plugins/utils/artifact-parser.md) — Pipeline artifact/definition file parser and validator

## Tests

* [Test Suite](/tests/test-suite.md) — Unit and integration test organization
