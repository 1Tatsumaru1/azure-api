from collections import defaultdict
from unittest import result
import azure.functions as func
import pandas as pd
import numpy as np
import pickle
import json
import time
import io


# Source : https://github.com/NicolasHug/Surprise/blob/master/examples/top_n_recommendations.py
def get_top_n_art(predictions, deja_lus, n=5):
    """
    Renvoi les n articles les plus recommandées pour chaque utilisateur parmis ceux non lus
        @param predictions <Surprise Prediction> : prédictions issues de la méthode "test" d'un modèle Surprise
        @param deja_lus <list> : liste des articles déjà lus par l'utilisateur
        @param n <int> : nombre de recommandations à émettre
        @return <dict> : dictionnaire {user_id: [(category_id, predicted_rating), ...]}
    """
    # Map the predictions to each user
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        if iid not in deja_lus:
            top_n[uid].append((iid, est))

    # Sort the predictions for each user and retrieve the k highest ones
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]

    return top_n


def make_recommandation(model, user_id, art_by_user, art_df, n=5):
    """
    Renvoi les articles les plus recommandés pour un utilisateur donné
        @param model <Surprise.SVD> : model entraîné servant à la prédiction
        @param user_id <int> : utilisateur pour qui effectuer la prédiction
        @param art_by_user <Pandas.DataFrame> : dataframe des interactions utilisateur/article
        @param art_df <Pandas.DataFrame> : dataframe listant les articles et leur catégorie
        @param n <int> : nombre d'articles à renvoyer (défaut : 5)
        @return <list>, <list>, <list>, <list> : articles prédits, articles consultés, catégories prédites,
            catégories consultées
    """
    # Constuction du dataset de prédiction
    article_list = art_by_user['article_id'].unique()
    user_fill = np.full((len(article_list),), user_id)
    value_fill = np.full((len(article_list),), 0)
    art_rating = pd.DataFrame({
        'user_id': user_fill,
        'article_id': article_list,
        'value': value_fill
    })
    
    # Identifiation des articles lus
    user_art_list = art_by_user[art_by_user['user_id'] == user_id]['article_id'].values
    art_rating.loc[art_rating['article_id'].isin(user_art_list), 'value'] = 1
    
    # Récupération de la prédiction
    pred = model.test(art_rating.to_numpy())
    top_n = get_top_n_art(pred, user_art_list)
    
    # Préparation des données retournées
    pred_arts = [art for art, _ in top_n[user_id]]
    pred_cats = list(set(art_df[art_df['article_id'].isin(pred_arts)]['category_id'].values))
    
    return ", ".join([str(c) for c in list(set(pred_cats))]), ",".join([str(a) for a in pred_arts])


def main(
    req: func.HttpRequest,
    artDf: func.InputStream,
    artByUser: func.InputStream,
    svdModel: func.InputStream) -> func.HttpResponse:

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
        model = pickle.loads(svdModel.read())
        art_by_user = pd.read_csv(io.StringIO(artByUser.read().decode('utf-8')))
        art_df = pd.read_csv(io.StringIO(artDf.read().decode('utf-8')))
        t_load = time.time()

        # Prédiction
        cats, arts = make_recommandation(model, user_id, art_by_user, art_df)
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
