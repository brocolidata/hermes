## Development guidelines

### Setup Environment
1. Install dependencies by running
```
uv sync --all-extras
```


### Create Lambda layer
1. Create the layer folder
```bash
mkdir -p lambda_layer/python
```
2. Generate the requirements.txt that will be used to fill the layer folder
```bash
uv export --extra aws-essentials --no-dev --format requirements-txt > lambda_layer_requirements.txt
```

3. Fill the layer folder
```bash
uv pip install --target=lambda_layer/python -r lambda_layer_requirements.txt
```

4. Add the Hermes source code to the layer folder
```bash
cp -r /hermes/hermes lambda_layer/python/lib/python3.12/site-packages/
```

```bash
cp -r /hermes/hermes lambda_layer/python/
```


4. Zip the layer folder
```bash
zip -r lambda_layer.zip ./lambda_layer/python/
```

