import logging

from azure.storage.blob import BlobServiceClient, BlobClient
import azure.functions as func
import pandas as pd
import numpy as np
import json
import os
import io


###############################################################################################

#connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
#blob_client = BlobClient.from_connection_string(connect_str)
#blob_service_client = BlobServiceClient.from_connection_string(connect_str)
#container_client = blob_service_client.create_container(container_name)
#blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)
#with open(upload_file_path, "rb") as data:
#    blob_client.upload_blob(data)

#download_file_path = os.path.join(local_path, str.replace(local_file_name ,'.txt', 'DOWNLOAD.txt'))
#container_client = blob_service_client.get_container_client(container= container_name) 

##################################################################################################

def main(req: func.HttpRequest, artDf: func.InputStream) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    art_df = pd.read_csv(io.StringIO(artDf.read().decode('utf-8')))

    if name:
        return func.HttpResponse(f"Hello, {json.dumps(art_df.iloc[0, :].to_list())}.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
