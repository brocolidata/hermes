# ⚙️ Configuration Overview

Hermes is configured using YAML files located in your **configuration folder**.

By default, this folder is defined in `hermes_config.yml`:

```yaml
project_paths:
  configuration_folder: ./configuration
```

---

## 📁 Configuration Structure

A Hermes project is composed of one or more YAML files:

```bash
configuration/
├── sources.yml
├── destinations.yml
└── pipelines.yml
```

You can organize your configuration however you like:

* one file per resource
* or a single file for everything

---

## 🧩 Supported Definitions

Each YAML file can contain one or more of the following sections:

```yaml
sources:
  - ...

destinations:
  - ...

pipelines:
  - ...
```

---

## 🔗 Cross-References

Hermes configurations are **linked together by name**:

* Pipelines reference **sources**
* Pipelines reference **destinations**

Example:

```yaml
pipelines:
  - name: my_pipeline
    sources:
      - name: my_source
        tables: [table1]
    destinations:
      - my_destination
```

---

## 📦 Merging Configuration Files

All YAML files in the configuration folder are:

1. Loaded
2. Merged
3. Validated

This allows you to split configuration across multiple files.

---

## 🧠 Key Principles

* Definitions are **declarative**
* Resources are **referenced by name**
* Configuration is **environment-independent**
* Execution logic lives in **connectors**, not YAML

---

## ➡️ Next Steps

* Learn about [Sources](sources/custom.md)
* Learn about [Destinations](destinations/object_storage.md)
* Learn about [Pipelines](pipelines.md)
