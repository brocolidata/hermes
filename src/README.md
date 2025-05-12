## Development guidelines

### Setup Environment
1. Install dependencies by running
```
uv sync --all-extras --all-groups
```


### Create Lambda layer
1. Create the layer folder
```bash
mkdir -p lambda_layer/python
```
2. Generate the requirements.txt that will be used to fill the layer folder
```bash
uv export --all-extras --no-extra ingestion_core --no-dev --no-editable --format requirements-txt > lambda_layer_requirements.txt
```

3. Fill the layer folder
```bash
uv pip install --target=lambda_layer/python -r lambda_layer_requirements.txt
```




4. Zip the layer folder
```bash
zip -r lambda_layer.zip ./lambda_layer/python/
```

