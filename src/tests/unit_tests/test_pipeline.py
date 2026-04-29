from unittest.mock import MagicMock, patch

import omegaconf
import pytest

from hermes.exceptions import PipelineError
from hermes.pipeline import Pipeline, get_pipeline

PIPELINE_NAME = "sync_float_rates"


@pytest.fixture
def pipeline_config(set_hermes_project_folder, demo_config):
    pipeline_config = list(
        filter(lambda p: p.name == PIPELINE_NAME, demo_config["pipelines"])
    )[0]
    return pipeline_config


@pytest.fixture
def mock_source_connector():
    """Fixture to create a mocked source connector."""
    mock_connector = MagicMock()
    mock_connector.name = "float_rates"
    mock_connector.extract.return_value = {"float_rates": "raw_data"}
    mock_connector.process_data.return_value = "processed_data"
    mock_connector._get_table_config.return_value = {"data_key": "float_rates"}
    return mock_connector


@pytest.fixture
def mock_destination_connector():
    """Fixture to create a mocked destination connector."""
    mock_connector = MagicMock()
    mock_connector.name = "landing_zone"
    mock_connector.data_stage = "processed"
    return mock_connector


@patch("hermes.connectors.get_connector")
def test_pipeline_initialization(mock_get_connector, pipeline_config):
    """Test pipeline initialization and attribute setup."""
    mock_get_connector.side_effect = lambda config, _: MagicMock()
    pipeline = Pipeline(pipeline_config)

    assert pipeline.pipeline_name == "sync_float_rates"
    assert pipeline.schedule == "0 20 * * 1-5"
    assert pipeline.sources_tables == {"float_rates": ["dirham_change_rates"]}
    assert pipeline.destinations_names == ["landing_zone", "demo_athena_iceberg"]


@patch("hermes.utils.get_definitions_from_file")
def test_get_pipeline_success(mock_get_definitions):
    """Test get_pipeline function when pipeline exists."""
    mock_get_definitions.return_value = omegaconf.OmegaConf.create(
        {"pipelines": [{"name": "sync_float_rates"}, {"name": "another_pipeline"}]}
    )
    with patch("hermes.pipeline.Pipeline", return_value=MagicMock()) as mock_pipeline:
        pipeline = get_pipeline("sync_float_rates")
        assert pipeline is mock_pipeline.return_value


@patch("hermes.utils.get_definitions_from_file")
def test_get_pipeline_not_found(mock_get_definitions):
    """Test get_pipeline function when pipeline does not exist."""
    mock_get_definitions.return_value = omegaconf.OmegaConf.create(
        {"pipelines": [{"name": "another_pipeline"}]}
    )
    ERROR_MSG = """error during configuration retrieval for pipeline sync_float_rates.
            error : sync_float_rates configuration cannot be found
        """
    with pytest.raises(PipelineError, match=ERROR_MSG):
        get_pipeline("sync_float_rates")
