from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from omegaconf import DictConfig

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
                "module_path": "float_rates_extractor.py",
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
        assert source.config.module_path == "float_rates_extractor.py"
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
