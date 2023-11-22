import omegaconf
import pandas as pd
from hermes import connectors, settings, utils


class Pipeline:


    def __init__(self, pipeline: omegaconf.dictconfig.DictConfig):
        self.pipeline_config = pipeline
        self.pipeline_name = pipeline.name
        self.schedule = pipeline.schedule
        self.source_name = pipeline.source
        self.source_connector = self._get_source_connector()
        self.destination_name = pipeline.destination
        self.destination_connector = self._get_destination_connector()


    def _get_connector(self, meta_type: settings.ConnectorsMetaTypes):
        connectors_meta_types = [c.value for c in settings.ConnectorsMetaTypes]
        if meta_type not in connectors_meta_types:
            raise ValueError(
                'source_or_destination must be one of "source" or "destination"'
            )
        definitions = utils.get_definitions_from_file()
        match meta_type:
            case 'source':
                source_path = definitions.sources.get(self.source_name)
                if not source_path:
                    raise ValueError(f'{self.source_name} source cannot be found.')
                source_config_file = utils.load_config(source_path)
                source_config = list(
                    filter(
                        lambda s: s.name == self.source_name,
                        source_config_file.sources
                    )
                )[0]
                connector = connectors.get_source_connector(source_config)
            case 'destination':
                destination_path = definitions.destinations.get(self.destination_name)
                if not destination_path:
                    raise ValueError(
                        f'{self.destination_name} destination cannot be found.'
                    )
                destination_config_file = utils.load_config(destination_path)
                destination_config = list(
                    filter(
                        lambda d: d.name == self.destination_name,
                        destination_config_file.destinations
                    )
                )[0]
                connector = connectors.get_destination_connector(destination_config)
        return connector 
                    
    
    def _get_source_connector(self):
        return self._get_connector('source')
    

    def _get_destination_connector(self):
        return self._get_connector('destination')
    

    def run_extract(self) -> dict[str, pd.DataFrame]:
        """Run the extract step of the pipeline and get its ouputs

        Returns:
            dict[str, pd.DataFrame]: Data extracted from source
        """
        dc_outputs = self.source_connector.extract()
        return dc_outputs
    
    
    def run_load(self, dc_extract_outputs:dict[str, pd.DataFrame]):
        """Run the load step of the pipeline

        Args:
            dc_extract_outputs (dict[str, pd.DataFrame]): Data extracted from source
        """
        self.destination_connector.load(dc_extract_outputs)

    
    def run(self):
        """Run all steps of the pipeline
        """
        dc_extract_outputs = self.run_extract()
        self.run_load(dc_extract_outputs)


def get_pipeline(pipeline_name: str) -> Pipeline:
    """Get pipeline object.

    Args:
        pipeline_name (str): Name of the pipeline defined in a configuration file

    Raises:
        ValueError: The pipeline can't be found

    Returns:
        Pipeline: Corresponding pipeline object
    """
    definitions = utils.get_definitions_from_file()
    pipelines = definitions.pipelines
    if pipeline_name not in pipelines:
        raise ValueError(f'{pipeline_name} pipeline does not exist')
    pipeline_path = definitions.pipelines.get(pipeline_name)
    pipeline_config_file = utils.load_config(pipeline_path)
    pipeline_config = list(
        filter(
            lambda p: p.name == pipeline_name,
            pipeline_config_file.pipelines
        )
    )[0]
    pipeline_obj = Pipeline(pipeline_config)
    return pipeline_obj