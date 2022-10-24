import logging

import azure.functions as func
import pandas as pd
import numpy as np
import json
import os


connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')


def main(req: func.HttpRequest, artDf) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    art_df = pd.read_csv(artDf)

    if name:
        return func.HttpResponse(f"Hello, {json.dumps(art_df.iloc[0, :].to_list())}.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
