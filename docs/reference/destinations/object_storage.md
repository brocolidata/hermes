# 🪣 Object Storage Destination

This destination writes data to an object storage system.

Supported backends:
- `local_storage`
- `s3`

---

## 📌 Configuration

```yaml
destinations:
  - name: my_destination
    description: Store data
    type: local_storage
    config:
      format: json
      bucket: ./artefacts/data
````

---

## 🔑 Fields

### Destination

| Key           | Description               | Required |
| ------------- | ------------------------- | -------- |
| `name`        | Destination name          | yes      |
| `description` | Description               | yes      |
| `type`        | `local_storage` or `s3`   | yes      |
| `config`      | Destination configuration | yes      |

---

### Config

| Key      | Description                             | Required |
| -------- | --------------------------------------- | -------- |
| `format` | Output format (`json`, `parquet`, etc.) | yes      |
| `bucket` | Storage location                        | yes      |

---

## 🧠 Notes

* For `local_storage`, `bucket` is a local folder path
* For `s3`, `bucket` is the S3 bucket name
