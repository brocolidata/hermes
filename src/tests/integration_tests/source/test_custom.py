from hermes.pipeline import get_pipeline

TEST_PIPELINE_NAME = "sync_float_rates"


def test_custom_source(
    set_aws_env_vars,
    mock_fsspec_open,
    mock_athena_to_iceberg,
):
    # hermes.run_pipeline(TEST_PIPELINE_NAME)
    pipeline = get_pipeline(TEST_PIPELINE_NAME)
    print("hello")
