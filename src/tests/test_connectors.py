import os
import pathlib

import omegaconf
import pytest

import hermes


def get_test_pipelines():
    config_folder = os.getenv('HERMES_CONFIG_FOLDER')
    CONFIG_FILE = "test_pipelines.yml"
    config_file_path = pathlib.Path(config_folder, CONFIG_FILE)
    config = omegaconf.OmegaConf.load(config_file_path)
    pipeline_names = [p.name for p in config.pipelines]
    return pipeline_names
    

@pytest.fixture()
def patch_destination_load(monkeypatch):
    def patch_load(*args, **kwargs):
        pass
    monkeypatch.setattr(
        hermes.destinations.object_storage.ObjectStorageDestination,
        "load",
        patch_load
    )

@pytest.mark.parametrize('pipeline_name', get_test_pipelines())
def test_pipelines(patch_destination_load, pipeline_name):
    patch_destination_load
    hermes.extract_load(pipeline_name)


def test_extract(patch_destination_load):
    TEST_PIPELINE_NAME = 'sync_sales'
    patch_destination_load
    from hermes.pipeline import get_pipeline
    pipeline = get_pipeline(TEST_PIPELINE_NAME)
    print('pipeline_name')