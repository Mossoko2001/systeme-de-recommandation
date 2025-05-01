import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import pickle

class ContentBasedRecommender:
    def __init__(self, dataframe, text_columns=['description'], weights=None, 
                 item_id_col='item_id', cache_dir=None):
        """
        Initialise le système de recommandation basé sur le contenu.
        
        Args:
            dataframe: DataFrame contenant les données des items
            text_columns: Liste des colonnes textuelles à utiliser pour la recommandation
            weights: Poids à attribuer à chaque colonne textuelle (égaux par défaut)
            item_id_col: Nom de la colonne contenant l'ID unique de l'item
            cache_dir: Répertoire pour mettre en cache la matrice de similarité
        """
        self.df = dataframe
        self.text_columns = text_columns if isinstance(text_columns, list) else [text_columns]
        self.weights = weights if weights else [1.0] * len(self.text_columns)
        self.item_id_col = item_id_col
        self.cache_dir = cache_dir
        self.vectorizers = {}
        self.similarity_matrix = None
        
        # Vérification de la validité des données
        for col in self.text_columns:
            if col not in self.df.columns:
                raise ValueError(f"La colonne '{col}' n'existe pas dans le DataFrame")
        if self.item_id_col not in self.df.columns:
            raise ValueError(f"La colonne ID '{self.item_id_col}' n'existe pas dans le DataFrame")
            
        # Nettoyage des données textuelles
        for col in self.text_columns:
            self.df[col] = self.df[col].fillna('').astype('U')
            
        self._fit()
        
    def _preprocess_text(self, text):
        """Prétraite le texte pour améliorer la qualité des recommandations"""
        # Enlève les caractères spéciaux et les espaces inutiles
        text = text.replace(r'[^a-zA-Z0-9\s]', '')  # enlever les caractères spéciaux
        text = text.replace(r'\s+', ' ')  # enlever les espaces multiples
        text = text.strip()  # enlever les espaces au début et à la fin
        return text.lower()
        
    def _fit(self):
        """Calcule la matrice de similarité entre les items"""
        # Essaie de charger la matrice de similarité du cache si elle existe
        if self.cache_dir and os.path.exists(os.path.join(self.cache_dir, 'similarity_matrix.pkl')):
            try:
                with open(os.path.join(self.cache_dir, 'similarity_matrix.pkl'), 'rb') as f:
                    self.similarity_matrix = pickle.load(f)
                print("Matrice de similarité chargée depuis le cache")
                return
            except Exception as e:
                print(f"Erreur lors du chargement du cache: {e}")
        
        # Crée une matrice TF-IDF pour chaque colonne textuelle
        tfidf_matrices = []
        
        for col in self.text_columns:
            vectorizer = TfidfVectorizer(stop_words='english', 
                                         max_features=5000,
                                         ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform(self.df[col].apply(self._preprocess_text))
            self.vectorizers[col] = vectorizer
            tfidf_matrices.append(tfidf_matrix)
            
        # Combine les matrices avec leurs poids respectifs
        if len(tfidf_matrices) == 1:
            combined_matrix = tfidf_matrices[0]
        else:
            # Normalise les poids
            weights = np.array(self.weights) / sum(self.weights)
            combined_matrix = np.zeros((self.df.shape[0], self.df.shape[0]))
            
            # Calcule la similarité pondérée
            for i, matrix in enumerate(tfidf_matrices):
                sim_matrix = cosine_similarity(matrix)
                combined_matrix += weights[i] * sim_matrix
                
        self.similarity_matrix = combined_matrix
        
        # Sauvegarde la matrice de similarité dans le cache si nécessaire
        if self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)
            with open(os.path.join(self.cache_dir, 'similarity_matrix.pkl'), 'wb') as f:
                pickle.dump(self.similarity_matrix, f)
                
    def recommend(self, item_id, top_n=5, filters=None):
        """
        Recommande des items similaires à l'item spécifié.
        
        Args:
            item_id: ID de l'item pour lequel faire des recommandations
            top_n: Nombre de recommandations à retourner
            filters: Dictionnaire de filtres à appliquer {colonne: valeur}
            
        Returns:
            DataFrame avec les items recommandés, triés par similarité
        """
        if item_id not in self.df[self.item_id_col].values:
            raise ValueError(f"L'item avec l'ID {item_id} n'existe pas.")
            
        idx = self.df.index[self.df[self.item_id_col] == item_id][0]
        
        # Récupère les scores de similarité
        similarity_scores = list(enumerate(self.similarity_matrix[idx]))
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        
        # Exclut l'item lui-même
        similarity_scores = [(i, score) for i, score in similarity_scores if i != idx ]
        
        # Applique les filtres si spécifiés
        filtered_indices = range(len(self.df))
        if filters:
            for col, value in filters.items():
                if col in self.df.columns:
                    if isinstance(value, list):
                        filtered_indices = [i for i in filtered_indices if self.df.iloc[i][col] in value]
                    else:
                        filtered_indices = [i for i in filtered_indices if self.df.iloc[i][col] == value]
                        
        filtered_scores = [(i, score) for i, score in similarity_scores if i in filtered_indices ]
        
        # Sélectionne les meilleurs matches
        top_matches = filtered_scores[:top_n]  
        
        # Crée un DataFrame de résultats avec score de similarité
        recommended_items = self.df.iloc[[i[0] for i in top_matches]].copy()
        recommended_items['similarity_score'] = [i[1] for i in top_matches]
        
        return recommended_items.sort_values('similarity_score', ascending=False)
        
    def evaluate(self, test_items, actual_similar_items, top_n=10):
        """
        Évalue la qualité des recommandations à partir d'un ensemble de test.
        
        Args:
            test_items: Liste d'IDs d'items à tester
            actual_similar_items: Dictionnaire {item_id: [liste d'items similaires connus]}
            top_n: Nombre de recommandations à considérer
            
        Returns:
            Dictionnaire de métriques d'évaluation
        """
        precision_scores = []
        recall_scores = []
        
        for item_id in test_items:
            if item_id not in self.df[self.item_id_col].values:
                continue
                
            try:
                recommended = self.recommend(item_id, top_n=top_n)
                recommended_ids = set(recommended[self.item_id_col].values)
                
                actual = set(actual_similar_items.get(item_id, []))
                
                # Calcul de la précision et du rappel
                if recommended_ids:
                    precision = len(actual.intersection(recommended_ids)) / len(recommended_ids)
                    precision_scores.append(precision)
                
                if actual:
                    recall = len(actual.intersection(recommended_ids)) / len(actual)
                    recall_scores.append(recall)
                    
            except Exception as e:
                print(f"Erreur lors de l'évaluation pour l'item {item_id}: {e}")
                
        # Calcul des métriques moyennes
        avg_precision = sum(precision_scores) / len(precision_scores) if precision_scores else 0
        avg_recall = sum(recall_scores) / len(recall_scores) if recall_scores else 0
        f1 = 2 * (avg_precision * avg_recall) / (avg_precision + avg_recall) if (avg_precision + avg_recall) > 0 else 0
        
        return {
            'precision': avg_precision,
            'recall': avg_recall,
            'f1_score': f1,
            'num_evaluated': len(precision_scores)
        }
    