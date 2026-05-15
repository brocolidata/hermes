# >_ CLI Commands

## List available pipelines

```bash
hermes pipeline list
```

## Debug your environment

```bash
hermes debug
```

This shows:

* Installed connectors
* Configuration paths
* System information

## Install connectors

```bash
hermes install
```

Interactive selection of available connectors.

## Parse Hermes artifacts
**⚠️ Before running a pipeline you should execute this command**

```bash
hermes artefact-parse
```



Reads all YAML config files from HERMES_CONFIG_FOLDER, merges them into a single definitions object, validates the merged config against the JSON schema, and generates a definitions.json file inside HERMES_ARTIFACTS_FOLDER.

This `definitions.json` is the runtime source used by `hermes pipeline run`.


## Displays current Hermes version.
```bash
hermes --version
```

## Shows all available commands
```bash
hermes --help
```
