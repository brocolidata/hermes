from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from omegaconf import DictConfig

from hermes.exceptions import CustomSourceError
from hermes.sources.custom import CustomSource


@pytest.fixture
def test_source_config():
    """Fixture to create a test source configuration."""
    return DictConfig(
        {
            "name": "float_rates_source",
            "description": "Test source for float rates",
            "config": {
                "extractor": "FloatRatesSourceExtractor",
                "module_path": "change_rates.py",
                "tables": [
                    {
                        "name": "float_rates",
                        "kwargs": {
                            "endpoint": "https://api.exchangeratesapi.io/latest"
                        },
                    }
                ],
            },
        }
    )


@pytest.fixture
def mock_extractor():
    """Mocked extractor for testing."""
    extractor = MagicMock()
    extractor.extract.return_value = {"float_rates": {"USD": 1.0, "EUR": 0.85}}
    extractor.process_data.return_value = pd.DataFrame(
        [{"currency": "USD", "rate": 1.0}, {"currency": "EUR", "rate": 0.85}]
    )
    return extractor


def test_custom_source_initialization(test_source_config):
    """Test that CustomSource initializes correctly."""
    with patch.object(
        CustomSource, "_get_extractor", return_value=lambda: MagicMock()
    ) as mock_get_extractor:
        source = CustomSource(test_source_config)
        assert source.name == "float_rates_source"
        assert source.description == "Test source for float rates"
        assert source.config.extractor == "FloatRatesSourceExtractor"
        assert source.config.module_path == "change_rates.py"
        assert len(source.output_tables) == 1
        assert source.output_tables[0].name == "float_rates"
        mock_get_extractor.assert_called_once()


@patch.object(CustomSource, "_get_extractor")
def test_custom_source_extract(mock_get_extractor, test_source_config, mock_extractor):
    """Test the extract method of CustomSource."""
    # Ensure `_get_extractor()` returns a function that returns `mock_extractor`
    mock_get_extractor.return_value = lambda: mock_extractor

    # Initialize CustomSource
    source = CustomSource(test_source_config)

    # Call extract
    extracted_data = source.extract("float_rates")

    # Validate extraction call
    mock_extractor.extract.assert_called_once_with(
        endpoint="https://api.exchangeratesapi.io/latest"
    )

    # Validate extracted data structure
    assert isinstance(extracted_data, dict)
    assert "float_rates" in extracted_data
    assert extracted_data["float_rates"] == {"USD": 1.0, "EUR": 0.85}


@patch.object(CustomSource, "_get_extractor")
def test_custom_source_process_data(
    mock_get_extractor, test_source_config, mock_extractor
):
    """Test the process_data method of CustomSource."""
    # Ensure `_get_extractor()` returns a function that returns `mock_extractor`
    mock_get_extractor.return_value = lambda: mock_extractor

    # Initialize CustomSource
    source = CustomSource(test_source_config)

    # Mock extracted data
    extracted_data = {"float_rates": {"USD": 1.0, "EUR": 0.85}}

    # Call process_data
    processed_data = source.process_data(extracted_data)

    # Validate process_data call
    mock_extractor.process_data.assert_called_once_with(extracted_data)

    # Validate processed data structure
    assert isinstance(processed_data, pd.DataFrame)
    assert processed_data.shape == (2, 2)  # Expecting 2 rows (USD, EUR) and 2 columns


def test_custom_source_extractor_module_not_found(test_source_config):
    """Test that CustomSource raises an exception when the extractor function is not found."""
    failing_source_config = test_source_config.copy()
    failing_source_config.config.extractor = "DoesNotExist"
    ERROR_MSG = """Custom Source: error during initialization for source float_rates_source.
            error : DoesNotExist function cannot be found in /hermes/tests/assets/custom/change_rates.py
        """
    with pytest.raises(CustomSourceError, match=ERROR_MSG):
        CustomSource(failing_source_config)


def test_custom_source_extractor_not_found(test_source_config):
    """Test that CustomSource raises an exception when the extractor function is not found."""
    failing_source_config = test_source_config.copy()
    failing_source_config.config.extractor = "DoesNotExist"
    ERROR_MSG = """Custom Source: error during initialization for source float_rates_source.
            error : DoesNotExist function cannot be found in /hermes/tests/assets/custom/change_rates.py
        """
    with pytest.raises(CustomSourceError, match=ERROR_MSG):
        CustomSource(failing_source_config)


@patch.object(CustomSource, "_get_extractor", return_value=lambda: MagicMock())
def test_custom_source_table_not_found(mock_get_extractor, test_source_config):
    """Test that CustomSource raises an exception when table config is missing."""
    source = CustomSource(test_source_config)
    ERROR_MSG = """Custom Source: error during extraction for source float_rates_source.
            error : missing_table table configuration cannot be found in float_rates_source output tables
        """
    with pytest.raises(CustomSourceError, match=ERROR_MSG):
        source.extract("missing_table")


@patch.object(CustomSource, "_get_extractor")
def test_custom_source_extract_exception(mock_get_extractor, test_source_config):
    """Test that CustomSource.extract raises an exception on extractor failure."""
    mock_extractor = MagicMock()
    mock_extractor.extract.side_effect = Exception("Extraction failed")
    mock_get_extractor.return_value = lambda: mock_extractor
    source = CustomSource(test_source_config)
    ERROR_MSG = """Custom Source: error during extracting for source float_rates_source.
            error : Extraction failed
        """
    with pytest.raises(CustomSourceError, match=ERROR_MSG):
        source.extract("float_rates")


@patch.object(CustomSource, "_get_extractor")
def test_custom_source_process_data_exception(mock_get_extractor, test_source_config):
    """Test that CustomSource.process_data raises an exception on processing failure."""
    mock_extractor = MagicMock()
    mock_extractor.process_data.side_effect = Exception("Processing failed")
    mock_get_extractor.return_value = lambda: mock_extractor
    source = CustomSource(test_source_config)
    ERROR_MSG = """Custom Source: error during data processing for source float_rates_source.
            error : Processing failed
        """
    with pytest.raises(CustomSourceError, match=ERROR_MSG):
        source.process_data({"float_rates": {"USD": 1.0, "EUR": 0.85}})
