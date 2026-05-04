from hermes import logging_utils
from hermes import pipeline as pipeline_utils

logger = logging_utils.get_logger()


def run_pipeline(pipeline_name: str):
    """Run a pipeline

    Args:
        pipeline_name (str): Name of the pipeline to run
    """
    logger.info(f"Running {pipeline_name} pipeline...")
    pipeline = pipeline_utils.get_pipeline(pipeline_name)
    pipeline_run = pipeline.create_run()
    pipeline_run.run()
    logger.info(f"Successfully run {pipeline_name} pipeline")
