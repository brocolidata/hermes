![Hermes banner](/hermes_banner.jpg)

A simple Serverless-compatible data Extract-Load framework.

***⚠️ This is an Alpha project, we don't recommend using it in production ⚠️***

# Installation
TBD

# Project configuration 🧰
A working Hermes project requires to define : 
- A **Hermes configuration folder**, via the `HERMES_CONFIG_FOLDER` environment variable
- A **Hermes artifact folder**, via the `HERMES_ARTIFACTS_FOLDER` environment variable
- A **Hermes custom connectors folder**, via the `HERMES_CUSTOM_CONNECTORS_FOLDER` environment variable

# Hermes configuration files ⚙️
Hermes nodes are configured in `.yml` files located in the **Hermes configuration folder**.
We can configure 3 types of nodes : 
- **Sources 🛫** : Where the data is extracted from
- **Destinations 🛬** : Where the data is loaded to
- **Pipelines ✈️** : A data pipeline that combines a source & a destination 

## Source configuration 🛫
Sources configuration are defined under the `sources:` list :

| Configuration key    | Description                                                   | Required |
|---------------------|---------------------------------------------------------------|----------|
| `name`              | name of the source                                            | yes      |
| `description`       | description of the source                                     | yes      |
| `type`              | type of the source. See TBD                                   | yes      |
| `config`             | configuration for the source. See corresponding configuration | yes      |

**Supported sources (`type:`)** : 
- [CustomSource](#customsource) 🛠️ : Extract data using a custom Python function

### CustomSource 🛠️
To use this source : 
- set the type of the [Source configuration](#source-configuration) to `custom`
- define the following keys under `config:` :

| Configuration key    | Description                                                                  | Required |
|---------------------|------------------------------------------------------------------------------|----------|
| `function_name`     | Name of the entrypoint function to get data from the source                  | yes      |
| `module_path`       | Module path relative to HERMES_CUSTOM_CONNECTORS_FOLDER                      | yes      |
| `kwargs`            | Dict of keyword argument name (as key) and keyword argument value (as value) | yes      |
| `outputs`           | Dict of output (as key) and pandas.DataFrame (as value)                      | yes      |

## Destination configuration 🛬
Destinations configuration are defined under the `destinations:` list :

| Configuration key | Description                                                        | Required |
|-------------------|--------------------------------------------------------------------|----------|
| name              | name of the destination                                            | yes      |
| description       | description of the destination                                     | yes      |
| type              | type of the destination. See TBD                                   | yes      |
| config            | configuration for the destination. See corresponding configuration | yes      |

**Supported destinations (`type:`)** : 
- [ObjectStorage](#customsource) 🪣 : Load data to an object storage bucket (GCS/S3)


### ObjectStorage 🪣
To use this source : 
- set the type of the [Destination configuration](#destination-configuration) to `object_storage`
- define the following keys under `config:` :

| Configuration key | Description                                              | Required |
|-------------------|----------------------------------------------------------|----------|
| service           | Name of the service. See supported services              | yes      |
| format            | File format used to load data. See supported file format | yes      |
| bucket            | Destination bucket                                       | yes      |

**Supported services (`service:`)** : 
- `gcs`

**Supported format (`format:`)** : 
- `parquet`

## Pipeline configuration ✈️
Pipelines configuration are defined under the `pipelines:` list :

| Configuration key | Description                                                      | Required |
|-------------------|------------------------------------------------------------------|----------|
| `name`            | name of the pipeline                                             | yes      |
| `source`          | source of the pipeline, it must be a configured source           | yes      |
| `destination`     | destination of the pipeline, it must be a configured destination | yes      |
| `schedule`        | A CRON schedule                                                  | yes      |