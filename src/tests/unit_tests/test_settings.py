import pytest

from hermes.exceptions import ConfigLoadError
from hermes.settings import (
    get_artifacts_folder,
    get_config_folder,
    get_custom_connectors_folder,
)


def test_get_config_folder_exception(monkeypatch):
    monkeypatch.delenv("HERMES_CONFIG_FOLDER")
    with pytest.raises(
        ConfigLoadError, match="HERMES_CONFIG_FOLDER environment variable must be set"
    ):
        get_config_folder()


def test_get_artifacts_folder_exception(monkeypatch):
    monkeypatch.delenv("HERMES_ARTIFACTS_FOLDER")
    with pytest.raises(
        ConfigLoadError,
        match="HERMES_ARTIFACTS_FOLDER environment variable must be set",
    ):
        get_artifacts_folder()


def test_get_custom_connectors_folder_exception(monkeypatch):
    monkeypatch.delenv("HERMES_CUSTOM_CONNECTORS_FOLDER")
    with pytest.raises(
        ConfigLoadError,
        match="HERMES_CUSTOM_CONNECTORS_FOLDER environment variable must be set",
    ):
        get_custom_connectors_folder()
