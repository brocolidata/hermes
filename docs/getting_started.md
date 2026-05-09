
# 🚀 Getting Started

This guide walks you through creating and running your first **Hermes pipeline** using the Hermes CLI.

By the end, you will:
- Initialize a Hermes project
- Define a source, destination, and pipeline
- Run your first pipeline

---

## 1. Installation

```bash
pip install "git+https://github.com/astral-sh/ruff"
```

---

## 2. Initialize a Hermes Project

The easiest way to get started is using the CLI:

```bash
hermes init
```

This will:

* Create a project structure
* Generate a `hermes_config.yml` file
* Optionally install connectors

### Generated structure

```bash
.
├── configuration/
├── artefacts/
├── custom_connectors/
└── hermes_config.yml
```

### Configuration file

```yaml
project_paths:
  configuration_folder: ./configuration
  artefacts_folder: ./artefacts
  custom_connectors_folder: ./custom_connectors
```

👉 Hermes uses this file to locate your project folders.

---

## 3. Create Your First Pipeline Configuration

Inside the `configuration/` folder, create a file:

```bash
configuration/demo.yml
```

---

## 4. Define a Source 🛫

```yaml
sources:
  - name: currency_api
    description: Fetch currency exchange rates
    type: custom
    config:
      extractor: CurrencyExtractor
      module_path: custom_connectors.currency
      tables:
        - name: rates
          data_key: rates
          kwargs:
            endpoint: "https://www.floatrates.com/daily/mad.json"
```

---

## 5. Define a Destination 🛬

```yaml
destinations:
  - name: local_output
    description: Store data locally
    type: local_storage
    config:
      format: json
      bucket: ./artefacts/data
```

---

## 6. Define a Pipeline ✈️

```yaml
pipelines:
  - name: currency_pipeline
    sources:
      - name: currency_api
        tables: [rates]
    destinations:
      - local_output
    schedule: "0 12 * * *"
```

---

## 7. Implement the Extractor

Create the file:

```bash
custom_connectors/currency.py
```

```python
import requests


class CurrencyExtractor:
    def extract(self, **kwargs):
        endpoint = kwargs["endpoint"]
        response = requests.get(endpoint)
        data = response.json()

        return {
            "rates": list(data.values())
        }
```

---

## 8. Run Your Pipeline

```bash
hermes pipeline run currency_pipeline
```

You should see:

```bash
Running pipeline: currency_pipeline
Pipeline currency_pipeline completed successfully!
```

---

## 9. Inspect the Output

Your data is now available in:

```bash
./artefacts/data/
```

Example:

```bash
artefacts/data/rates.json
```

---

## 🔍 Useful CLI Commands

### List available pipelines

```bash
hermes pipeline list
```

---

### Debug your environment

```bash
hermes debug
```

This shows:

* Installed connectors
* Configuration paths
* System information

---

### Install connectors

```bash
hermes install
```

Interactive selection of available connectors.

---

## 🎉 Success!

You just ran your first Hermes pipeline.

---

## 🧠 What’s Next?

* Explore the **Configuration Reference**
* Build more advanced sources
* Use cloud destinations like S3 or Athena Iceberg

---

## 🛠️ Manual Setup (Optional)

If you prefer not to use the CLI, you can manually define:

```bash
export HERMES_CONFIG_FOLDER=./configuration
export HERMES_ARTIFACTS_FOLDER=./artefacts
export HERMES_CUSTOM_CONNECTORS_FOLDER=./custom_connectors
```

However, using `hermes init` is recommended.
