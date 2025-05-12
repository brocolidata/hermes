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
| `kwargs`         | Dictionary of keyword arguments for the extractor. Supports referencing [destination variables](#destination-variables-).             | yes      |

---

Example : 
```yaml
tables:
  - name: dirham_change_rates
    data_key: float_rates
    kwargs:
      endpoint: 'https://www.floatrates.com/daily/mad.json'
      last_date: $destinations.demo_athena_iceberg.variables.last_date

```


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

### Destination Variables 📦
Hermes supports destination-level variables that can be queried at runtime and used inside your extraction logic — typically to enable incremental loading.

These variables are defined as SQL queries in the destination config and can be referenced in source extractor kwargs. Hermes will evaluate these queries before the extraction phase and inject the values into the source configuration.

To reference a destination variable in a source: `$destinations.<destination_name>.variables.<variable_name>`

Example:
```
last_date: $destinations.demo_athena_iceberg.variables.last_date
```
The variable's value is injected before executing the extractor, so you can use it to query data since the last loaded timestamp, filter only new entries, etc.

### ObjectStorageDestination 🪣  
To use this destination:  
- Set the type of the [Destination configuration](#destination-configuration) to `object_storage`  
- Define the following keys under `config:`  

| Configuration Key  | Description                                              | Required |
|--------------------|----------------------------------------------------------|----------|
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
| `variables` | Optional variables to query from the destination before extraction. Each variable must define a SQL query. | no |

---

Example : 
```yaml
- name: demo_athena_iceberg
  type: athena_iceberg
  config:
    glue_database: raw_glue_database
    table_location: s3://a-bucket/table-location
    temp_path: s3://a-bucket/hermes-temp-path
  variables:
    last_date:
      query: SELECT MAX(date) FROM {this}

```
- `{this}` will be replaced with the full table identifier.
- The result of the query will be used as a variable in source connectors that reference it.

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