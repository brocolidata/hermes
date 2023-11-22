from hermes import logging_utils, utils
from hermes import pipeline as pipeline_utils

logger = logging_utils.get_logger()

def extract_load(pipeline_name: str):
    logger.info('Parsing Hermes project...')
    utils.parse_project()
    logger.info(f'Running {pipeline_name} pipeline...')
    pipeline = pipeline_utils.get_pipeline(pipeline_name)
    pipeline.run()
    logger.info(f'Successfully run {pipeline_name} pipeline')
