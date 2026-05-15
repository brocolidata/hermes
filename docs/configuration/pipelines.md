
# ✈️ Pipelines

A pipeline defines how data flows from sources to destinations.

---

## 📌 Configuration

```yaml
pipelines:
  - name: my_pipeline
    sources:
      - name: my_source
        tables: [table1]
    destinations:
      - my_destination
    schedule: "0 12 * * *"
```

---

## 🔑 Fields

| Key            | Description          | Required |
| -------------- | -------------------- | -------- |
| `name`         | Pipeline name        | yes      |
| `sources`      | List of sources      | yes      |
| `destinations` | List of destinations | yes      |
| `schedule`     | CRON expression      | yes      |

---

## 📦 Sources

Each source:

```yaml
- name: my_source
  tables: [table1, table2]
```

---

## 📦 Destinations

List of destination names:

```yaml
destinations:
  - my_destination
```

---

## ⏱️ Scheduling

Examples:

* `"0 12 * * *"` → every day at 12:00 UTC
* `"0 20 * * 1-5"` → weekdays at 20:00 UTC

---

## 🧠 Execution Flow

1. Extract data from sources
2. Process tables
3. Load into destinations
