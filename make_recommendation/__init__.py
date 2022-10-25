import azure.functions as func
import pandas as pd
import json
import time
import io


def main(
    req: func.HttpRequest,
    recoDf: func.InputStream) -> func.HttpResponse:

    # Récupération du user_id
    user_id = req.params.get('user_id')
    if not user_id:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            user_id = req_body.get('user_id')

    # Si user_id : chargement des fichiers et prédiction
    if user_id:

        # Chargement des fichiers
        t_start = time.time()
        reco_df = pd.read_csv(io.StringIO(recoDf.read().decode('utf-8')), sep=";")
        t_load = time.time()

        # Prédiction
        ligne = reco_df[reco_df['user_id'] == int(user_id)]
        cats = ligne['reco_cat'].values[0]
        arts = ligne['reco_art'].values[0]
        t_pred = time.time()

        # Résultat
        result = {
            'user_id': user_id,
            'reco_cats': cats,
            'reco_arts': arts,
            't_start': t_start,
            't_load': t_load,
            't_pred': t_pred
        }

    # Sinon réponse standard
    else:
        result = {
            'user_id': '',
            'reco_cats': '[]',
            'reco_arts': '[]',
            't_start': 0,
            't_load': 0,
            't_pred': 0
        }

    return func.HttpResponse(json.dumps(result))
