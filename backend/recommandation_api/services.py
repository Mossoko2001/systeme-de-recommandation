import os

import pandas as pd
from . import collaborative
from . import content_based
from . import hybrid
dataset_dir = '../../datasets/'
script_dir = os.path.dirname(__file__)
dataset_path = os.path.abspath(os.path.join(script_dir, dataset_dir))

# Fonction pour charger les datasets dynamiquement
def load_datasets(dataset_type):
    if dataset_type == 'books':
        content_df = pd.read_csv(f'{dataset_path}/books/books_enriched.csv', usecols=["book_id", "best_book_id", "isbn","authors", "title", "description", "genres", "small_image_url"])
        content_df = content_df.rename(columns={'book_id': 'item_id'})
        content_df = content_df.drop_duplicates('title', ignore_index=True) # Suppression des titres doublons
        
        ratings_df = pd.read_csv(f'{dataset_path}/books/ratings.csv', nrows=500000)
        ratings_df = ratings_df.rename(columns={'book_id': 'item_id'})
        # Supprimer les multiples notations d'un meme livre par un utilisateur
        ratings_df = ratings_df.drop_duplicates(subset=['item_id', 'user_id'], ignore_index=True,  keep='last')

        # Calculer le nombre de notes par item
        item_counts = ratings_df['item_id'].value_counts()
        # Garder uniquement les item_id qui ont été notés au moins 5 fois
        items_to_keep = item_counts[item_counts >= 5].index
        # Filtrer le dataset   F:\recommandation_system_G6\datasets\movies\movies.csv
        ratings_df = ratings_df[ratings_df['item_id'].isin(items_to_keep)]
    elif dataset_type == 'movies':  
        content_df = pd.read_csv(f'{dataset_path}/movies/movies.csv')
        content_df = content_df.rename(columns={'movieId': 'item_id'})

        tags_df = pd.read_csv(f'{dataset_path}/movies/tags.csv')
        tags_df = tags_df.rename(columns={'userId': 'user_id', 'movieId': 'item_id'})

        content_df.drop_duplicates(subset=['title'], inplace=True)    # Supprimer les doublons
        # Assosier les deux datasets pour avoirs la tags sur les films
        content_df = content_df.merge(tags_df, on='item_id', how='left').fillna(" ")
        content_df['genres'] = content_df.genres.apply(lambda x : x.replace('|', ' '))
        content_df.drop_duplicates(subset=['item_id'], ignore_index=True, inplace=True)

        ratings_df = pd.read_csv(f'{dataset_path}/movies/ratings.csv')
        ratings_df = ratings_df.rename(columns={'userId': 'user_id', 'movieId': 'item_id'})
        ratings_df = ratings_df.drop_duplicates(subset=['item_id', 'user_id'], keep='last', ignore_index=True)
        # Calculer le nombre de notes par item
        item_counts = ratings_df['item_id'].value_counts()
        # Garder uniquement les item_id qui ont été notés au moins 3 fois
        items_to_keep = item_counts[item_counts >= 10].index
        # Filtrer le dataset
        ratings_df = ratings_df[ratings_df['item_id'].isin(items_to_keep)].copy()
    else:
        raise ValueError("Invalid dataset type")
    return content_df, ratings_df

def build_hybrid_recommender(dataset_type, weight_content=0.5, weight_collaborative=0.5):
    content_df, ratings_df = load_datasets(dataset_type)
    if dataset_type == 'books':
        text_columns = ['description','genres', 'title']
    else:
        text_columns = ['title','genres', 'tag']
    content_recommender = content_based.ContentBasedRecommender(
        dataframe=content_df,
        text_columns=text_columns,
        weights= [0.4, 0.3, 0.3],
        cache_dir=f'{dataset_path}/{dataset_type}/content/'    
    )
    collaborative_recommender = collaborative.CollaborativeFilteringRecommender(
        ratings_df=ratings_df,
        method='item_based',
        n_factors=50,
        cache_dir=f'{dataset_path}/{dataset_type}/collaborative/'
    )

    hybrid_recommender = hybrid.HybridRecommender(
        content_recommender=content_recommender,
        collaborative_recommender=collaborative_recommender,
        weight_content=weight_content,
        weight_collaborative=weight_collaborative,
        item_data= content_df
    )
    return hybrid_recommender
