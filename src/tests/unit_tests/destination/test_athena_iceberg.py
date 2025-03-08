import pandas as pd
import pytest
from omegaconf import DictConfig

from hermes.destinations.athena_iceberg import AthenaIcebergDestination

# @pytest.fixture
# def mock_athena_to_iceberg():
#     """Fixture to mock awswrangler.athena.to_iceberg."""
#     with patch("awswrangler.athena.to_iceberg") as mock_to_iceberg:
#         yield mock_to_iceberg


@pytest.fixture
def test_destination_config():
    """Fixture to create a test destination config."""
    return DictConfig(
        {
            "config": {
                "glue_database": "test_db",
                "table_location": "s3://test-bucket/",
            }
        }
    )


@pytest.fixture
def test_dataframe():
    """Fixture to create a test DataFrame."""
    return pd.DataFrame({"id": [1, 2, 3], "value": ["A", "B", "C"]})


def test_load_data(mock_athena_to_iceberg, test_destination_config, test_dataframe):
    """Test the load method of AthenaIcebergDestination."""
    destination = AthenaIcebergDestination(test_destination_config)

    # Call load method
    destination.load("test_source", "test_table", test_dataframe)

    # Validate `to_iceberg` call
    mock_athena_to_iceberg.assert_called_once_with(
        df=test_dataframe,
        database="dl_raw_test_source",  # Should match f"dl_raw_{source_name}"
        table="test_table",
        table_location="s3://test-bucket/",
        temp_path="",
    )
