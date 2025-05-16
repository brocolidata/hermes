import omegaconf

from hermes import logging_utils, settings

logger = logging_utils.get_logger()


def get_definitions_from_file() -> omegaconf.dictconfig.DictConfig:
    definition_file_path = settings.get_definition_file_path()
    definitions = omegaconf.OmegaConf.load(definition_file_path)
    return definitions
