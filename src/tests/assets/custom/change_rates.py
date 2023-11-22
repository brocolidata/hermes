import pandas as pd
import requests as rq


def get_dirham_change_rates(endpoint: str) -> pd.DataFrame:
    response = rq.get(endpoint)
    dc_raw_data = response.json()
    df = pd.DataFrame(list(dc_raw_data.values()))
    return {
        "df":df
    }

    