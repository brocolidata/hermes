![Hermes banner](/hermes_banner.jpg)

A simple Serverless-compatible data Extract-Load framework.

***⚠️ This is an Alpha project, we don't recommend using it in production ⚠️***

# Installation
TBD

# Hermes project Configuration 🧰  
A working Hermes project requires defining:  
- A **Hermes configuration folder**, via the `HERMES_CONFIG_FOLDER` environment variable  
- A **Hermes artifact folder**, via the `HERMES_ARTIFACTS_FOLDER` environment variable  
- A **Hermes custom connectors folder**, via the `HERMES_CUSTOM_CONNECTORS_FOLDER` environment variable  

# Hermes Configuration Files ⚙️  
Hermes nodes are configured in `.yml` files located in the **Hermes configuration folder**.  
Each file can contain one or more of the following node types:  
- **Sources 🛫**: Where the data is extracted from  
- **Destinations 🛬**: Where the data is loaded to  
- **Pipelines ✈️**: A data pipeline that connects sources & destinations  

## Source Configuration 🛫  
Sources are defined under the `sources:` list:

| Configuration Key  | Description                                                   | Required |
|--------------------|---------------------------------------------------------------|----------|
| `name`            | Name of the source                                            | yes      |
| `description`     | Description of the source                                     | yes      |
| `type`           | Type of the source. See supported sources                      | yes      |
| `config`         | Configuration for the source. See corresponding source type    | yes      |

**Supported sources (`type:`)**:  
- [CustomSource](#customsource) 🛠️: Extract data using a custom Python function  

### CustomSource 🛠️  
To use this source:  
- Set the type of the [Source configuration](#source-configuration) to `custom`  
- Define the following keys under `config:`  

| Configuration Key  | Description                                                              | Required |
|--------------------|--------------------------------------------------------------------------|----------|
| `extractor`       | The extractor class name                                                | yes      |
| `module_path`     | Path to the Python module implementing the extractor                     | yes      |
| `tables`          | List of tables extracted from the source                                | yes      |

Each table in `tables` has the following structure:

| Configuration Key  | Description                                                 | Required |
|--------------------|-------------------------------------------------------------|----------|
| `name`            | Name of the table                                            | yes      |
| `data_key`        | Key in the extracted data corresponding to this table        | yes      |
| `kwargs`         | Dictionary of keyword arguments for the extractor            | yes      |

---

## Destination Configuration 🛬  
Destinations are defined under the `destinations:` list:

| Configuration Key | Description                                                        | Required |
|------------------|--------------------------------------------------------------------|----------|
| `name`          | Name of the destination                                            | yes      |
| `description`   | Description of the destination                                     | yes      |
| `type`         | Type of the destination. See supported destinations                | yes      |
| `config`       | Configuration for the destination. See corresponding destination type | yes      |

**Supported destinations (`type:`)**:  
- [ObjectStorageDestination](#objectstoragedestination) 🪣: Load data to an object storage bucket (S3/GCS)  
- [AthenaIcebergDestination](#athenaicebergdestination) ❄️: Load data into an Athena Iceberg table  

### ObjectStorageDestination 🪣  
To use this destination:  
- Set the type of the [Destination configuration](#destination-configuration) to `object_storage`  
- Define the following keys under `config:`  

| Configuration Key  | Description                                              | Required |
|--------------------|----------------------------------------------------------|----------|
| `service`         | Name of the service (`s3` or `gcs`)                       | yes      |
| `format`         | File format used to load data (`json`, `parquet`, etc.)    | yes      |
| `bucket`         | Destination bucket name                                    | yes      |

### AthenaIcebergDestination ❄️  
To use this destination:  
- Set the type of the [Destination configuration](#destination-configuration) to `athena_iceberg`  
- Define the following keys under `config:`  

| Configuration Key  | Description                                               | Required |
|--------------------|-----------------------------------------------------------|----------|
| `glue_database`   | The AWS Glue database where the Iceberg table is stored   | yes      |
| `table_location`  | The S3 path where the table data is stored                 | yes      |
| `temp_path`       | Temporary path in S3 for query execution                   | yes      |

---

## Pipeline Configuration ✈️  
Pipelines are defined under the `pipelines:` list:

| Configuration Key  | Description                                                      | Required |
|--------------------|------------------------------------------------------------------|----------|
| `name`            | Name of the pipeline                                             | yes      |
| `sources`        | List of sources for the pipeline. Must match a configured source | yes      |
| `destinations`   | List of destinations. Must match a configured destination        | yes      |
| `schedule`       | A CRON schedule for execution                                    | yes      |

Each source in `sources` has the following structure:

| Configuration Key  | Description                                      | Required |
|--------------------|--------------------------------------------------|----------|
| `name`            | Name of the source (must match a defined source)  | yes      |
| `tables`          | List of table names extracted from the source     | yes      |

Each destination in `destinations` is a string referring to an existing destination.

**Example CRON schedules (`schedule:`)**:
- `"0 12 * * *"` → Run every day at 12:00 UTC
- `"0 20 * * 1-5"` → Run at 20:00 UTC, Monday to Friday