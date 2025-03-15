import pandas as pd
import pytest
from omegaconf import DictConfig

from hermes.destinations.athena_iceberg import AthenaIcebergDestination


@pytest.fixture
def test_destination_config():
    """Fixture to create a test destination config."""
    return DictConfig(
        {
            "name": "demo_athena_iceberg",
            "config": {
                "glue_database": "raw_glue_database",
                "table_location": "s3://a-bucket/table-location",
                "temp_path": "s3://a-bucket/temp-path",
            },
        }
    )


@pytest.fixture
def test_dataframe():
    """Fixture to create a test DataFrame."""
    return pd.DataFrame({"id": [1, 2, 3], "value": ["A", "B", "C"]})


def test_load_data(mock_athena_to_iceberg, test_destination_config, test_dataframe):
    """Test the load method of AthenaIcebergDestination."""
    destination = AthenaIcebergDestination(test_destination_config)

    assert destination.name == "demo_athena_iceberg"

    # Call load method
    destination.load("test_source", "test_table", test_dataframe)

    # Validate `to_iceberg` call
    mock_athena_to_iceberg.assert_called_once_with(
        df=test_dataframe,
        database="raw_glue_database",
        table="test_table",
        table_location="s3://a-bucket/table-location/test_source/test_table/",
        temp_path="s3://a-bucket/temp-path/test_source/test_table/",
    )
