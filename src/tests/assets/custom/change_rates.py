import pandas as pd
import requests as rq

from hermes.sources.custom import CustomSourceExtractor

OUTPUT_NAME = "float_rates"


class FloatRatesSourceExtractor(CustomSourceExtractor):
    def extract(self, endpoint):
        response = rq.get(endpoint)
        raw_data = response.json()
        return {OUTPUT_NAME: raw_data}

    def process_data(self, output_dc: dict) -> dict[str, pd.DataFrame]:
        raw_data = output_dc[OUTPUT_NAME]
        df = pd.DataFrame(list(raw_data.values()))
        return df
