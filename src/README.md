## Development guidelines

### Setup Environment
1. Create virtual environment by running
```
uv venv
```

2. Activate virtual environment by selecting the right python executable in VS Code (`./.venv/bin/python`)

3. Install dependencies by running
```
uv sync --all-extras --all-groups
```

### Create a plugin
1. `cd` into the plugin subfolder depending on the type of plugin : 
- `plugins/sources` : source connectors
- `plugins/destinations` : destination connectors
- `plugins/utils` : other plugins
2. 


### Create Lambda layer
1. Create the layer folder
```bash
mkdir -p lambda_layer/python
```
2. Generate the requirements.txt that will be used to fill the layer folder
```bash
uv export --extra custom_source --extra s3_destination_core --extra athena_iceberg_destination --no-dev --no-editable --format requirements-txt > lambda_layer_requirements.txt
```

3. Fill the layer folder
```bash
uv pip install --target=lambda_layer/python -r lambda_layer_requirements.txt
```




4. Zip the layer folder
```bash
zip -r lambda_layer.zip ./lambda_layer/python/
```

