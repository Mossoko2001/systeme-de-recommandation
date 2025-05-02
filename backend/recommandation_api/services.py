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


# ----- mes fonctions de recommandation -----

def get_content_based_movies_datasets():
    movies_df = pd.read_csv('../../../datasets/movies/movies.csv')
    movies_df = movies_df.rename(columns={'movieId': 'item_id'})

    tags_df = pd.read_csv('../../../datasets/movies/tags.csv')
    tags_df = tags_df.rename(columns={'userId': 'user_id', 'movieId': 'item_id'})

    movies_df.drop_duplicates(subset=['title'], inplace=True)    # Supprimer les doublons
    # Assosier les deux datasets pour avoirs la tags sur les films
    movies_tags_df = pd.merge(movies_df, tags_df, on='item_id', how='left').fillna(" ")
    movies_tags_df['genres'] = movies_tags_df.genres.apply(lambda x : x.replace('|', ' '))
    movies_tags_df.drop_duplicates(subset=['item_id'], ignore_index=True, inplace=True)

    ratings = pd.read_csv('../../../datasets/movies/ratings.csv')
    ratings = ratings.rename(columns={'userId': 'user_id', 'movieId': 'item_id'})
    ratings = ratings.drop_duplicates(subset=['item_id', 'user_id'], keep='last', ignore_index=True)
    # Calculer le nombre de notes par item
    item_counts = ratings['item_id'].value_counts()
    # Garder uniquement les item_id qui ont été notés au moins 5 fois
    items_to_keep = item_counts[item_counts >= 10].index
    # Filtrer le dataset
    ratings = ratings[ratings['item_id'].isin(items_to_keep)].copy()
    
    return movies_tags_df

def get_movies_recommended_content_based(item_id, top_n):
    movies_df = get_content_based_movies_datasets()

    recomander = content_based.ContentBasedRecommender(dataframe=movies_df, text_columns=['title','genres', 'tag'], item_id_col='item_id', cache_dir='../../../datasets/movies/', weights=[0.4, 0.3, 0.3])
    results = recomander.recommend(item_id=item_id, top_n=top_n)
    results = results.to_dict('records') # Convertir en dictionnaire pour la sérialisation
    # Afficher les résultats
    print(f"Les films similaire au film d'id {item_id} :")
    for item in results:
        print(f"Identifiant film: {item['item_id']} %Similarité: {item['similarity_score']} Titre: {item['title']} Genres: {item['genres']}")

# Fonctions des livres
def get_content_based_books_dataset():
    books_df = pd.read_csv('../../../datasets/books_datasets/books_enriched.csv', usecols=["book_id", "best_book_id", "isbn","authors", "title", "description", "genres", "small_image_url"])
    books_df = books_df.rename(columns={'book_id': 'item_id'})
    books_df = books_df.drop_duplicates('title') # Suppression des titres doublons


    return books_df

def get_books_recommended_content_based(item_id, top_n):
    books_df = get_content_based_books_dataset()

    recommender = content_based.ContentBasedRecommender(dataframe=books_df, text_columns=['description','genres', 'title'], item_id_col='item_id', cache_dir='../../../datasets/books_datasets/', weights=[0.5, 0.3, 0.2])
    
    results = recommender.recommend(item_id=item_id, top_n=top_n)
    print(f"Les livres similaire au livre d'id {item_id} :")
    results = results.to_dict('records') # Convertir en dictionnaire pour la sérialisation
    for item in results:
        print(f"Identifiant: {item['item_id']} %Similarité: {item['similarity_score']} Titre: {item['title']} Auteurs: {item['authors']} Genres: {item['genres']}")

# Les fonctions pour la recommandation collaborative
def get_movies_collaborative_dataset():
    movies = pd.read_csv('../../../datasets/movies/movies.csv')
    movies = movies.rename(columns={'userId': 'user_id', 'movieId': 'item_id'})
    movies = movies.drop_duplicates('title', ignore_index=True) # Suppression des titres doublons

    ratings = pd.read_csv('../../../datasets/movies/ratings.csv')
    ratings = ratings.rename(columns={'userId': 'user_id', 'movieId': 'item_id'})
    ratings = ratings.drop_duplicates(subset=['item_id', 'user_id'], keep='last', ignore_index=True)
    # Calculer le nombre de notes par item
    item_counts = ratings['item_id'].value_counts()
    # Garder uniquement les item_id qui ont été notés au moins 5 fois
    items_to_keep = item_counts[item_counts >= 10].index
    # Filtrer le dataset
    ratings = ratings[ratings['item_id'].isin(items_to_keep)].copy()

    return ratings, movies

def show_movies_recommanded(user_id, top_n, rec_method, similar_item=False, item_id=0):
    """
    Recupere les récommandation de films pour un utilisateurs donnée
    ou les fims similaire à un film donnée
    Args:
        uiser_id : ID de l'utiliateur pour le quel faire des recommandation
        top_n: Le nombre de recommandation à retourener
        rec_methode: la methode de recomamdation ('svd', 'user_based' ou 'item_based')
        similar_item: Demmande si c'est une recommandation de films similaire à un film donnée
        item_id: ID du film pour lequel on recommande les films similaire
    """
    ratings, movies = get_movies_collaborative_dataset()
    if rec_method == "svd":
        collaborative_svd = collaborative.CollaborativeFilteringRecommender(ratings_df=ratings, user_id_col='user_id', item_id_col='item_id', 
                    rating_col='rating', method='svd', n_factors=50, cache_dir='../../../datasets/movies/')
        if similar_item:
            recs = collaborative_svd.recommend_similar_items(item_id=item_id, top_n=top_n, item_data=movies)
        else:
            recs = collaborative_svd.recommend_for_user(user_id=user_id, top_n=top_n, exclude_rated=True, item_data=movies)
        
    elif rec_method == "user_based":
        collaborative_user_based = collaborative.CollaborativeFilteringRecommender(ratings_df=ratings, user_id_col='user_id', item_id_col='item_id', 
                rating_col='rating', method='user_based', n_factors=50, cache_dir='../../../datasets/movies/')
        recs = collaborative_user_based.recommend_for_user(user_id=user_id, top_n=top_n, exclude_rated=True, item_data=movies)
    elif rec_method == "item_based":
        collaborative_item_based = collaborative.CollaborativeFilteringRecommender(ratings_df=ratings, user_id_col='user_id', item_id_col='item_id', 
                rating_col='rating', method='item_based', n_factors=50, cache_dir='../../../datasets/movies/')
        if similar_item:
            recs = collaborative_item_based.recommend_similar_items(item_id=item_id, top_n=top_n, item_data=movies)
        else:
            recs = collaborative_item_based.recommend_for_user(user_id=user_id, top_n=top_n, exclude_rated=True, item_data=movies)
    if similar_item:
        print(f"Les films Similaires au film {item_id} :")
        recs = recs.to_dict('records')
        for item in recs:
            print(f"Identifiant film: {item['item_id']} %Similarité: {item['similarity']} Titre: {item['title']} Genres: {item['genres']}")
    else:
        print(f"Les films recommandé pour l'utilisateur {user_id} :")
        recs = recs.to_dict('records')
        for item in recs:
            print(f"Identifiant film: {item['item_id']} Score: {item['score']} Titre: {item['title']} Genres: {item['genres']}")
   

# Les fonctions pour les livres
def get_books_colaborative_dataset():
    """
    Charge le dataset movies Le dataset des livres pour la recommandation 
    collaborative. Harmonise les nom des colonnes, supprime les doublons

    Returns:
        Retourne deux DataFrame reatings_df , books_df
    """
    books_df = pd.read_csv('../../../datasets/books_datasets/books_enriched.csv', usecols=["book_id", "best_book_id", "isbn","authors", "title", "small_image_url"])
    books_df = books_df.rename(columns={'book_id': 'item_id'})
    books_df = books_df.drop_duplicates('title', ignore_index=True) # Suppression des titres doublons

    ratings_df = pd.read_csv('../../../datasets/books_datasets/ratings.csv', nrows=500000)
    ratings_df = ratings_df.rename(columns={'book_id': 'item_id'})
    # Supprimer les multiples notations d'un meme livre par un utilisateur
    ratings_df = ratings_df.drop_duplicates(subset=['item_id', 'user_id'], ignore_index=True,  keep='last')

    # Calculer le nombre de notes par item
    item_counts = ratings_df['item_id'].value_counts()
    # Garder uniquement les item_id qui ont été notés au moins 5 fois
    items_to_keep = item_counts[item_counts >= 5].index
    # Filtrer le dataset
    ratings_df = ratings_df[ratings_df['item_id'].isin(items_to_keep)]

    return ratings_df, books_df

def show_books_recommanded(user_id, top_n, rec_method, similar_item=False, item_id=0):
    """
    Recupere les récommandation de livres pour un utilisateurs donnée
    ou les livres similaire à un livre donnée (similar_item=True)
    Args:
        uiser_id : ID de l'utiliateur pour le quel faire des recommandation
        top_n: Le nombre de recommandation à retourener
        rec_methode: la methode de recomamdation ('svd', 'user_based' ou 'item_based')
        similar_item: Demmande si c'est une recommandation de livre similaire à un livre donnée
        item_id: ID du livre pour lequel on recommande les livres similaire
    """
    ratings, books = get_books_colaborative_dataset()

    if rec_method == "svd":
        collaborative_svd = collaborative.CollaborativeFilteringRecommender(ratings_df=ratings, user_id_col='user_id', item_id_col='item_id', 
                    rating_col='rating', method='svd', n_factors=50, cache_dir='../../../datasets/books_datasets/')
        if similar_item:
            recs = collaborative_svd.recommend_similar_items(item_id=item_id, top_n=top_n, item_data=books)
        else:
            recs = collaborative_svd.recommend_for_user(user_id=user_id, top_n=top_n, exclude_rated=True, item_data=books)
        
    elif rec_method == "user_based":
        collaborative_user_based = collaborative.CollaborativeFilteringRecommender(ratings_df=ratings, user_id_col='user_id', item_id_col='item_id', 
                rating_col='rating', method='user_based', n_factors=50, cache_dir='../../../datasets/books_datasets/')
        recs = collaborative_user_based.recommend_for_user(user_id=user_id, top_n=top_n, exclude_rated=True, item_data=books)
    elif rec_method == "item_based":
        collaborative_item_based = collaborative.CollaborativeFilteringRecommender(ratings_df=ratings, user_id_col='user_id', item_id_col='item_id', 
                rating_col='rating', method='item_based', n_factors=50, cache_dir='../../../datasets/books_datasets/')
        if similar_item:
            recs = collaborative_item_based.recommend_similar_items(item_id=item_id, top_n=top_n, item_data=books)
        else:
            recs = collaborative_item_based.recommend_for_user(user_id=user_id, top_n=top_n, exclude_rated=True, item_data=books)
    if similar_item:
        print(f"Les livres similaire à {item_id} :")
        recs = recs.to_dict('records')
        for item in recs:
            print(f"Identifiant livre: {item['item_id']} %Similarité: {item['similarity']} Titre: {item['title']} Auteurs: {item['authors']}")
    else:
        print(f"Les livres recommandé pour l'utilisateur {user_id} :")
        recs = recs.to_dict('records')
        for item in recs:
            print(f"Identifiant livre: {item['item_id']} Score: {item['score']} Titre: {item['title']} Auteurs: {item['authors']}")

# Exemple d'utilisation
# if __name__ == "__main__":
#     # Exporter les dataset et harmonisez les nom des colonnles
#     # Test content based collaborative 
#     # get_movies_recommended_content_based(item_id=2628, top_n=10)
#     # get_books_recommended_content_based(item_id=40, top_n=10)

#     # Test collaborative racommandation
#     # show_movies_recommanded(user_id=1, top_n=10, rec_method="item_based", similar_item=True, item_id=2628)
#     # show_books_recommanded(user_id=1, top_n=10, rec_method="svd", similar_item=True, item_id=2)

#     dataset_type = 'books'
#     hybrid_recomander = build_hybrid_recommender(dataset_type=dataset_type, weight_content=0.3, weight_collaborative=0.7)
#     recommended = hybrid_recomander.recommend_for_user(user_id=4, top_n=7)
#     recommended = recommended.to_dict(orient='records')
#     # print(recommended)
#     for item in recommended:
#         if dataset_type == 'books':
#             print(f"Identifiant livre: {item['item_id']} Score: {item['hybrid_score']} Titre: {item['title']} Auteurs: {item['authors']}")
#         else:
#             print(f"Identifiant film: {item['item_id']} Score: {item['hybrid_score']} Titre: {item['title']} Genres: {item['genres']}")