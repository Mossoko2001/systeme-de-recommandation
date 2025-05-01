# ----------------------- Version 2 -------------------------
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse.linalg import svds
import os
import pickle


class CollaborativeFilteringRecommender:
    """
    Système de recommandation basé sur le filtrage collaboratif.
    Utilise les interactions utilisateurs-items pour faire des recommandations.
    Implémente à la fois:
    - User-based collaborative filtering (UBCF)
    - Item-based collaborative filtering (IBCF)
    - Matrix factorization (SVD)
    """
    
    def __init__(self, ratings_df, user_id_col='user_id', item_id_col='item_id', 
                 rating_col='rating', method='svd', n_factors=50, cache_dir=None):
        """
        Initialise le système de recommandation par filtrage collaboratif.
        
        Args:
            ratings_df: DataFrame contenant les évaluations (user-item-rating)
            user_id_col: Nom de la colonne contenant l'ID utilisateur
            item_id_col: Nom de la colonne contenant l'ID de l'item
            rating_col: Nom de la colonne contenant la note
            method: Méthode de recommandation ('svd', 'user_based', ou 'item_based')
            n_factors: Nombre de facteurs latents pour SVD
            cache_dir: Répertoire pour mettre en cache les modèles
        """
        self.ratings_df = ratings_df
        self.user_id_col = user_id_col
        self.item_id_col = item_id_col
        self.rating_col = rating_col
        self.method = method
        self.n_factors = n_factors
        self.cache_dir = cache_dir
        
        # Vérification de la validité des données
        required_cols = [user_id_col, item_id_col, rating_col]
        for col in required_cols:
            if col not in self.ratings_df.columns:
                raise ValueError(f"La colonne '{col}' n'existe pas dans le DataFrame")
        
        # Créer les matrices utilisateur-item
        self.user_item_matrix = None
        self.item_user_matrix = None
        self.user_similarity = None
        self.item_similarity = None
        self.user_factors = None
        self.item_factors = None
        self.user_mapping = None
        self.item_mapping = None
        self.mean_ratings = None
        
        # Initialiser le modèle
        self._fit()
    
    def _create_matrix(self):
        """
        Crée la matrice d'évaluation utilisateur-item à partir du DataFrame.
        """
        # Créer un mapping des IDs aux indices de matrice
        unique_users = self.ratings_df[self.user_id_col].unique()
        unique_items = self.ratings_df[self.item_id_col].unique()
        
        self.user_mapping = {user_id: i for i, user_id in enumerate(unique_users)}
        self.item_mapping = {item_id: i for i, item_id in enumerate(unique_items)}
        
        # Créer une matrice éparse utilisateur-item
        self.user_item_matrix = np.zeros((len(unique_users), len(unique_items)))
        
        for _, row in self.ratings_df.iterrows():
            user_idx = self.user_mapping.get(row[self.user_id_col])
            item_idx = self.item_mapping.get(row[self.item_id_col])
            
            if user_idx is not None and item_idx is not None:
                self.user_item_matrix[user_idx, item_idx] = row[self.rating_col]
        
        # Créer la matrice transposée item-utilisateur
        self.item_user_matrix = self.user_item_matrix.T
        
        # Calculer la moyenne des évaluations par utilisateur
        self.mean_ratings = np.true_divide(
            self.user_item_matrix.sum(1),
            np.maximum(1, (self.user_item_matrix != 0).sum(1))
        )
    
    def _fit_svd(self):
        """
        Entraîne un modèle de recommandation par factorisation de matrice (SVD).
        """
        # Normaliser la matrice: soustraire la moyenne de chaque utilisateur
        normalized_matrix = self.user_item_matrix.copy()
        for i, mean in enumerate(self.mean_ratings):
            mask = normalized_matrix[i, :] != 0
            normalized_matrix[i, mask] -= mean
        
        # Décomposition SVD
        U, sigma, Vt = svds(normalized_matrix, k=min(self.n_factors, min(normalized_matrix.shape) - 1))
        
        # Convertir sigma en matrice diagonale
        sigma_diag = np.diag(sigma)
        
        # Stocker les matrices de facteurs
        self.user_factors = U
        self.item_factors = Vt.T
        
        # Stocker la matrice diagonale de valeurs singulières
        self.sigma = sigma_diag
        
        # Reconstruire la matrice de prédiction
        self.prediction_matrix = U.dot(sigma_diag).dot(Vt)
        
        # Ajouter les moyennes des utilisateurs
        for i, mean in enumerate(self.mean_ratings):
            self.prediction_matrix[i, :] += mean
    
    def _fit_user_based(self):
        """
        Entraîne un modèle de recommandation par filtrage collaboratif basé sur les utilisateurs.
        """
        # Calculer la similarité entre utilisateurs en utilisant la similarité cosinus
        self.user_similarity = cosine_similarity(self.user_item_matrix)
        
        # Pour chaque utilisateur, nous conservons uniquement les valeurs positives
        # et nous mettons à zéro la similarité de l'utilisateur avec lui-même
        for i in range(self.user_similarity.shape[0]):
            self.user_similarity[i, i] = 0
            self.user_similarity[i][self.user_similarity[i] < 0] = 0
    
    def _fit_item_based(self):
        """
        Entraîne un modèle de recommandation par filtrage collaboratif basé sur les items.
        """
        # Calculer la similarité entre items en utilisant la similarité cosinus
        self.item_similarity = cosine_similarity(self.item_user_matrix)
        
        # Pour chaque item, nous conservons uniquement les valeurs positives
        # et nous mettons à zéro la similarité de l'item avec lui-même
        for i in range(self.item_similarity.shape[0]):
            self.item_similarity[i, i] = 0
            self.item_similarity[i][self.item_similarity[i] < 0] = 0
    
    def _fit(self):
        """
        Entraîne le modèle de recommandation sélectionné.
        """
        # Essaie de charger le modèle du cache si disponible
        if self.cache_dir:
            cache_file = os.path.join(self.cache_dir, f'collaborative_{self.method}_model.pkl')
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'rb') as f:
                        cached_model = pickle.load(f)
                        for key, value in cached_model.items():
                            setattr(self, key, value)
                    print(f"Modèle collaboratif ({self.method}) chargé depuis le cache")
                    return
                except Exception as e:
                    print(f"Erreur lors du chargement du cache: {e}")
        
        # Créer la matrice utilisateur-item
        self._create_matrix()
        
        # Entraîner le modèle selon la méthode sélectionnée
        if self.method == 'svd':
            self._fit_svd()
        elif self.method == 'user_based':
            self._fit_user_based()
        elif self.method == 'item_based':
            self._fit_item_based()
        else:
            raise ValueError(f"Méthode de recommandation '{self.method}' non reconnue")
        
        # Sauvegarder le modèle dans le cache si nécessaire
        if self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)
            cache_file = os.path.join(self.cache_dir, f'collaborative_{self.method}_model.pkl')
            
            # Créer un dictionnaire avec les attributs à sauvegarder
            model_data = {
                'user_item_matrix': self.user_item_matrix,
                'item_user_matrix': self.item_user_matrix,
                'user_mapping': self.user_mapping,
                'item_mapping': self.item_mapping,
                'mean_ratings': self.mean_ratings
            }
            
            if self.method == 'svd':
                model_data.update({
                    'user_factors': self.user_factors,
                    'item_factors': self.item_factors,
                    'sigma': self.sigma,
                    'prediction_matrix': self.prediction_matrix
                })
            elif self.method == 'user_based':
                model_data['user_similarity'] = self.user_similarity
            elif self.method == 'item_based':
                model_data['item_similarity'] = self.item_similarity
            
            with open(cache_file, 'wb') as f:
                pickle.dump(model_data, f)
    
    def recommend_for_user(self, user_id, top_n=5, exclude_rated=True, item_data=None):
        """
        Recommande des items pour un utilisateur spécifique.
        
        Args:
            user_id: ID de l'utilisateur pour lequel faire des recommandations
            top_n: Nombre de recommandations à retourner
            exclude_rated: Exclure les items déjà évalués par l'utilisateur
            item_data: DataFrame optionnel contenant les informations sur les items
            
        Returns:
            DataFrame avec les items recommandés, triés par score
        """
        # Vérifier si l'utilisateur existe
        if user_id not in self.user_mapping:
            raise ValueError(f"L'utilisateur avec l'ID {user_id} n'existe pas.")
        
        user_idx = self.user_mapping[user_id]
        scores = None
        
        if self.method == 'svd':
            # Utiliser directement la matrice de prédiction
            scores = self.prediction_matrix[user_idx, :]
        
        elif self.method == 'user_based':
            # Calculer les scores en utilisant la similarité entre utilisateurs
            user_ratings = self.user_item_matrix[user_idx, :]
            user_sim = self.user_similarity[user_idx, :]
            
            # Pour chaque item non évalué, calculer une prédiction
            scores = np.zeros(self.user_item_matrix.shape[1])
            
            for item_idx in range(self.user_item_matrix.shape[1]):
                # Si l'utilisateur a déjà évalué cet item, on peut le sauter
                if user_ratings[item_idx] > 0 and exclude_rated:
                    scores[item_idx] = -np.inf
                    continue
                
                # Trouver tous les utilisateurs qui ont évalué cet item
                mask = self.user_item_matrix[:, item_idx] > 0
                
                # S'il n'y a pas d'évaluations pour cet item, continuer
                if not np.any(mask):
                    continue
                
                # Calculer la similarité pondérée
                weighted_sum = np.sum(user_sim[mask] * self.user_item_matrix[mask, item_idx])
                sim_sum = np.sum(np.abs(user_sim[mask]))
                
                # Éviter les divisions par zéro
                if sim_sum > 0:
                    scores[item_idx] = weighted_sum / sim_sum
                else:
                    scores[item_idx] = 0
        
        elif self.method == 'item_based':
            # Calculer les scores en utilisant la similarité entre items
            user_ratings = self.user_item_matrix[user_idx, :]
            scores = np.zeros(self.user_item_matrix.shape[1])
            
            # Trouver les items que l'utilisateur a évalués
            rated_items = np.where(user_ratings > 0)[0]
            
            for item_idx in range(self.user_item_matrix.shape[1]):
                # Si l'utilisateur a déjà évalué cet item, on peut le sauter
                if user_ratings[item_idx] > 0 and exclude_rated:
                    scores[item_idx] = -np.inf
                    continue
                
                # Calculer la similarité pondérée avec les items évalués
                item_sim = self.item_similarity[item_idx, rated_items]
                weighted_sum = np.sum(item_sim * user_ratings[rated_items])
                sim_sum = np.sum(np.abs(item_sim))
                
                # Éviter les divisions par zéro
                if sim_sum > 0:
                    scores[item_idx] = weighted_sum / sim_sum
                else:
                    scores[item_idx] = 0
        
        # Obtenir les indices des items avec les meilleurs scores
        if exclude_rated:
            # Masquer les items déjà évalués
            rated_mask = self.user_item_matrix[user_idx, :] > 0
            scores[rated_mask] = -np.inf
        
        # Obtenir les indices des items avec les meilleurs scores
        top_item_indices = np.argsort(scores)[::-1][:top_n]
        
        # Convertir les indices en IDs d'items
        reverse_item_mapping = {idx: item_id for item_id, idx in self.item_mapping.items()}
        recommended_items = [reverse_item_mapping[idx] for idx in top_item_indices]
        recommendation_scores = [scores[idx] for idx in top_item_indices]
        
        # Créer un DataFrame avec les résultats
        results = pd.DataFrame({
            self.item_id_col: recommended_items,
            'score': recommendation_scores
        })
        
        # Joindre les données d'items si fournies
        if item_data is not None:
            results = results.merge(item_data, on=self.item_id_col, how='left')
        
        return results.sort_values('score', ascending=False)
    
    def recommend_similar_items(self, item_id, top_n=5, item_data=None):
        """
        Recommande des items similaires à un item spécifié.
        Fonctionne uniquement avec la méthode item_based ou svd.
        
        Args:
            item_id: ID de l'item pour lequel faire des recommandations
            top_n: Nombre de recommandations à retourner
            item_data: DataFrame optionnel contenant les informations sur les items
            
        Returns:
            DataFrame avec les items recommandés, triés par similarité
        """
        if self.method not in ['item_based', 'svd']:
            raise ValueError("La recommandation d'items similaires n'est disponible qu'avec les méthodes 'item_based' ou 'svd'")
        
        # Vérifier si l'item existe
        if item_id not in self.item_mapping:
            raise ValueError(f"L'item avec l'ID {item_id} n'existe pas.")
        
        item_idx = self.item_mapping[item_id]
        similarity_scores = None
        
        if self.method == 'item_based':
            # Utiliser directement la matrice de similarité entre items
            similarity_scores = self.item_similarity[item_idx, :]
        
        elif self.method == 'svd':
            # Calculer la similarité cosinus entre les facteurs d'items
            item_factors = self.item_factors
            current_item_factors = item_factors[item_idx].reshape(1, -1)
            similarity_scores = cosine_similarity(current_item_factors, item_factors)[0]
        
        # Masquer l'item lui-même
        similarity_scores[item_idx] = -np.inf
        
        # Obtenir les indices des items les plus similaires
        top_item_indices = np.argsort(similarity_scores)[::-1][:top_n]
        
        # Convertir les indices en IDs d'items
        reverse_item_mapping = {idx: item_id for item_id, idx in self.item_mapping.items()}
        similar_items = [reverse_item_mapping[idx] for idx in top_item_indices]
        similarity_values = [similarity_scores[idx] for idx in top_item_indices]
        
        # Créer un DataFrame avec les résultats
        results = pd.DataFrame({
            self.item_id_col: similar_items,
            'similarity': similarity_values
        })
        
        # Joindre les données d'items si fournies
        if item_data is not None:
            results = results.merge(item_data, on=self.item_id_col, how='left')
        
        return results.sort_values('similarity', ascending=False)
    
    def evaluate(self, test_df, top_n=10):
        """
        Évalue la qualité des recommandations à partir d'un ensemble de test.
        
        Args:
            test_df: DataFrame contenant les interactions utilisateur-item de test
            top_n: Nombre de recommandations à considérer
            
        Returns:
            Dictionnaire de métriques d'évaluation
        """
        precision_sum = 0
        recall_sum = 0
        count = 0
        
        # Grouper les données de test par utilisateur
        test_grouped = test_df.groupby(self.user_id_col)
        
        for user_id, group in test_grouped:
            # Vérifier si l'utilisateur existe dans nos données d'entraînement
            if user_id not in self.user_mapping:
                continue
            
            # Obtenir les items que l'utilisateur a aimés dans l'ensemble de test
            actual_items = set(group[self.item_id_col].unique())
            
            try:
                # Prédire les recommandations pour cet utilisateur
                recommendations = self.recommend_for_user(user_id, top_n=top_n)
                recommended_items = set(recommendations[self.item_id_col].values)
                
                # Calculer les métriques
                if len(recommended_items) > 0:
                    precision = len(actual_items.intersection(recommended_items)) / len(recommended_items)
                    precision_sum += precision
                
                if len(actual_items) > 0:
                    recall = len(actual_items.intersection(recommended_items)) / len(actual_items)
                    recall_sum += recall
                
                count += 1
                
            except Exception as e:
                print(f"Erreur lors de l'évaluation pour l'utilisateur {user_id}: {e}")
        
        # Calculer les moyennes
        avg_precision = precision_sum / count if count > 0 else 0
        avg_recall = recall_sum / count if count > 0 else 0
        f1 = 2 * (avg_precision * avg_recall) / (avg_precision + avg_recall) if (avg_precision + avg_recall) > 0 else 0
        
        return {
            'precision': avg_precision,
            'recall': avg_recall,
            'f1_score': f1,
            'users_evaluated': count
        }

