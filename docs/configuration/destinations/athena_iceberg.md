# ❄️ Athena Iceberg Destination

This destination loads data into an **Apache Iceberg table** using AWS Athena.

---

## 📌 Configuration

```yaml
destinations:
  - name: my_iceberg
    description: Iceberg table
    type: athena_iceberg
    config:
      glue_database: my_database
      table_location: s3://bucket/path
      temp_path: s3://bucket/temp
```

---

## 🔑 Fields

### Config

| Key              | Description        | Required |
| ---------------- | ------------------ | -------- |
| `glue_database`  | Glue database name | yes      |
| `table_location` | S3 table location  | yes      |
| `temp_path`      | Athena temp path   | yes      |

---

## 🧠 Variables

You can define dynamic variables:

```yaml
variables:
  last_date:
    query: SELECT MAX(date) FROM {this}
```

* `{this}` is replaced with the table identifier
* The result can be reused in sources

---
