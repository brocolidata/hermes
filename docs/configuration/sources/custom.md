# 🛫 Custom Source

A **Custom Source** allows you to extract data using a Python class.

---

## 📌 Configuration

```yaml
sources:
  - name: my_source
    description: Example source
    type: custom
    config:
      extractor: MyExtractor
      module_path: custom_connectors.my_module
      tables:
        - name: my_table
          data_key: data
          kwargs:
            key: value
```

---

## 🔑 Fields

### Source

| Key           | Description               | Required |
| ------------- | ------------------------- | -------- |
| `name`        | Unique source name        | yes      |
| `description` | Description of the source | yes      |
| `type`        | Must be `custom`          | yes      |
| `config`      | Source configuration      | yes      |

---

### Config

| Key           | Description        | Required |
| ------------- | ------------------ | -------- |
| `extractor`   | Python class name  | yes      |
| `module_path` | Python module path | yes      |
| `tables`      | List of tables     | yes      |

---

### Tables

| Key        | Description                   | Required |
| ---------- | ----------------------------- | -------- |
| `name`     | Table name                    | yes      |
| `data_key` | Key in extracted data         | yes      |
| `kwargs`   | Arguments passed to extractor | yes      |

---

## 🧠 How It Works

1. Hermes imports the module from `module_path`
2. Instantiates the `extractor`
3. Calls its `extract(**kwargs)` method
4. Maps returned data using `data_key`

---

## 🧪 Example Extractor

```python
class MyExtractor:
    def extract(self, **kwargs):
        return {
            "data": [...]
        }
```
