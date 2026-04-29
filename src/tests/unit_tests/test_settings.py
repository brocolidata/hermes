import os
import tempfile
from pathlib import Path

import pytest

from hermes.exceptions import ConfigLoadError
from hermes.settings import (get_artifacts_folder, get_config_folder,
                             get_custom_connectors_folder)


def test_get_config_folder_exception(monkeypatch):
    # Remove environment variable and mock config file loading to raise FileNotFoundError
    monkeypatch.delenv("HERMES_CONFIG_FOLDER", raising=False)

    def mock_load_hermes_config_file():
        raise FileNotFoundError("Config file not found")

    monkeypatch.setattr("hermes.settings.load_hermes_config_file", mock_load_hermes_config_file)

    with pytest.raises(ConfigLoadError):
        get_config_folder()


def test_get_artifacts_folder_exception(monkeypatch):
    # Remove environment variable and mock config file loading to raise FileNotFoundError
    monkeypatch.delenv("HERMES_ARTIFACTS_FOLDER", raising=False)

    def mock_load_hermes_config_file():
        raise FileNotFoundError("Config file not found")

    monkeypatch.setattr("hermes.settings.load_hermes_config_file", mock_load_hermes_config_file)

    with pytest.raises(ConfigLoadError):
        get_artifacts_folder()


def test_get_custom_connectors_folder_exception(monkeypatch):
    # Remove environment variable and mock config file loading to raise FileNotFoundError
    monkeypatch.delenv("HERMES_CUSTOM_CONNECTORS_FOLDER", raising=False)

    def mock_load_hermes_config_file():
        raise FileNotFoundError("Config file not found")

    monkeypatch.setattr("hermes.settings.load_hermes_config_file", mock_load_hermes_config_file)

    with pytest.raises(ConfigLoadError):
        get_custom_connectors_folder()


def test_get_config_folder_returns_dict(monkeypatch):
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        monkeypatch.setenv("HERMES_CONFIG_FOLDER", temp_dir)
        result = get_config_folder()

        assert isinstance(result, dict)
        assert "path" in result
        assert "source" in result
        assert Path(result["path"]).resolve() == Path(temp_dir).resolve()
        assert result["source"] == "environment_variable"


def test_get_artifacts_folder_returns_dict(monkeypatch):
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        monkeypatch.setenv("HERMES_ARTIFACTS_FOLDER", temp_dir)
        result = get_artifacts_folder()

        assert isinstance(result, dict)
        assert "path" in result
        assert "source" in result
        assert Path(result["path"]).resolve() == Path(temp_dir).resolve()
        assert result["source"] == "environment_variable"


def test_get_custom_connectors_folder_returns_dict(monkeypatch):
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        monkeypatch.setenv("HERMES_CUSTOM_CONNECTORS_FOLDER", temp_dir)
        result = get_custom_connectors_folder()

        assert isinstance(result, dict)
        assert "path" in result
        assert "source" in result
        assert Path(result["path"]).resolve() == Path(temp_dir).resolve()
        assert result["source"] == "environment_variable"


def test_get_config_folder_with_create_if_missing(monkeypatch):
    # Test with a non-existing path but with create_if_missing=True
    with tempfile.TemporaryDirectory() as temp_dir:
        test_path = os.path.join(temp_dir, "new_config")
        monkeypatch.setenv("HERMES_CONFIG_FOLDER", test_path)
        result = get_config_folder(create_if_missing=True)

        assert isinstance(result, dict)
        assert "path" in result
        assert "source" in result
        assert os.path.exists(test_path)  # Should be created


def test_get_artifacts_folder_with_create_if_missing(monkeypatch):
    # Test with a non-existing path but with create_if_missing=True
    with tempfile.TemporaryDirectory() as temp_dir:
        test_path = os.path.join(temp_dir, "new_artifacts")
        monkeypatch.setenv("HERMES_ARTIFACTS_FOLDER", test_path)
        result = get_artifacts_folder(create_if_missing=True)

        assert isinstance(result, dict)
        assert "path" in result
        assert "source" in result
        assert os.path.exists(test_path)  # Should be created


def test_get_custom_connectors_folder_with_create_if_missing(monkeypatch):
    # Test with a non-existing path but with create_if_missing=True
    with tempfile.TemporaryDirectory() as temp_dir:
        test_path = os.path.join(temp_dir, "new_connectors")
        monkeypatch.setenv("HERMES_CUSTOM_CONNECTORS_FOLDER", test_path)
        result = get_custom_connectors_folder(create_if_missing=True)

        assert isinstance(result, dict)
        assert "path" in result
        assert "source" in result
        assert os.path.exists(test_path)  # Should be created


def test_get_config_folder_nonexistent_path_without_create(monkeypatch):
    # Test that ConfigLoadError is raised for non-existent paths when create_if_missing=False
    monkeypatch.setenv("HERMES_CONFIG_FOLDER", "/nonexistent/path")
    with pytest.raises(ConfigLoadError, match="does not exist"):
        get_config_folder(create_if_missing=False)


def test_get_artifacts_folder_nonexistent_path_without_create(monkeypatch):
    # Test that ConfigLoadError is raised for non-existent paths when create_if_missing=False
    monkeypatch.setenv("HERMES_ARTIFACTS_FOLDER", "/nonexistent/path")
    with pytest.raises(ConfigLoadError, match="does not exist"):
        get_artifacts_folder(create_if_missing=False)


def test_get_custom_connectors_folder_nonexistent_path_without_create(monkeypatch):
    # Test that ConfigLoadError is raised for non-existent paths when create_if_missing=False
    monkeypatch.setenv("HERMES_CUSTOM_CONNECTORS_FOLDER", "/nonexistent/path")
    with pytest.raises(ConfigLoadError, match="does not exist"):
        get_custom_connectors_folder(create_if_missing=False)
