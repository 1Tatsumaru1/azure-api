import logging

import azure.functions as func
import pandas as pd
import numpy as np
import json


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        test = pd.DataFrame({'name': [name], 'value': ['1']})
        return func.HttpResponse(f"Hello, {json.dumps(test.iloc[0, :].to_list())}.")
    else:
        test = np.array(['status', '200'])
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
