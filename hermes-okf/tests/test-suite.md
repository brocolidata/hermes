---
type: Test Suite
title: Hermes Test Suite
description: Unit and integration tests covering core modules, plugins, and CLI
resource: tests/
tags: [tests, pytest, quality]
status: stable
generated: { by: "pi/claude-sonnet-4-20250514", at: "2025-07-17T00:00:00Z" }
---

# Hermes Test Suite

Tests are organized under `tests/` using **pytest**. Dev dependencies include `moto` for AWS service mocking.

## Structure

```
tests/
├── conftest.py                              # Shared fixtures
├── test_pipelines.py                        # Pipeline integration test
├── unit_tests/
│   ├── test_connectors.py                   # Connector loader tests
│   ├── test_pipeline.py                     # Pipeline engine tests
│   ├── test_settings.py                     # Settings/config tests
│   ├── test_utils.py                        # Utility tests
│   ├── test_hermes_cli.py                   # CLI tests
│   ├── source/
│   │   └── test_custom.py                   # Custom source unit tests
│   └── destination/
│       ├── test_athena_iceberg.py            # Athena Iceberg unit tests
│       ├── test_object_storage.py            # Generic object storage unit tests
│       ├── test_s3.py                        # S3 destination unit tests
│       └── test_local_storage.py             # Local storage unit tests
├── integration_tests/
│   ├── source/
│   │   └── test_custom.py                   # Custom source integration tests
│   └── destination/
│       ├── test_athena_iceberg.py            # Athena Iceberg integration tests
│       └── test_object_storage.py            # Object storage integration tests
└── plugins/utils/
    └── test_hermes_artifact_parser/
        └── test_main.py                     # Artifact parser tests
```

## Test Assets

Located in `tests/assets/`:

| Asset                            | Purpose                                               |
|----------------------------------|-------------------------------------------------------|
| `artifacts/definitions.json`     | Sample definitions for various destination types      |
| `config/test_pipelines.yml`      | Sample pipeline YAML configuration                    |
| `custom/change_rates.py`         | Sample custom extractor function                      |
| `data/dirham_change_rates.json`  | Sample extraction output data                         |
| `hermes_config/hermes_config.yml`| Sample Hermes project configuration                   |
| `test_project/`                  | Complete sample project structure for integration tests|

## Test Tooling

| Tool    | Purpose                                |
|---------|----------------------------------------|
| `pytest`| Test runner                            |
| `moto`  | AWS service mocking (S3, Athena, Glue) |
