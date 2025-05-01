import pandas as pd
class HybridRecommender:
    def __init__(self, content_recommender, collaborative_recommender, 
                 weight_content=0.5, weight_collaborative=0.5, item_data=None):
        """
        Initialise le système de recommandation hybride.

        Args:
            content_recommender: Instance de ContentBasedRecommender
            collaborative_recommender: Instance de CollaborativeFilteringRecommender
            weight_content: Poids pour la recommandation basée sur le contenu
            weight_collaborative: Poids pour la recommandation collaborative
            item_data: Dataset des donnée
        """
        self.content_recommender = content_recommender
        self.collaborative_recommender = collaborative_recommender
        self.weight_content = weight_content
        self.weight_collaborative = weight_collaborative
        self.item_data = item_data

    def set_weights(self, weight_content, weight_collaborative):
        """
        Permet de mettre à jour les poids des recommandations.
        """
        self.weight_content = weight_content
        self.weight_collaborative = weight_collaborative

    def recommend_for_user(self, user_id, top_n=5):
        """
        Recommande des items à un utilisateur en combinant les deux systèmes.

        Args:
            user_id: ID de l'utilisateur
            top_n: Nombre de recommandations à retourner

        Returns:
            DataFrame avec les items recommandés et leur score hybride
        """
        # 1. Recommandations collaboratives
        collab_recs = self.collaborative_recommender.recommend_for_user(user_id, top_n=top_n*2)

        hybrid_scores = {}

        # 2. Combiner avec contenu
        for _, row in collab_recs.iterrows():
            item_id = row['item_id']
            collab_score = row.get('score', 1.0)

            # Cherche la similarité par contenu
            content_recs = self.content_recommender.recommend(item_id, top_n=1)
            if not content_recs.empty:
                content_score = content_recs.iloc[0].get('similarity', 1.0)
            else:
                content_score = 0

            # Score hybride
            hybrid_score = (self.weight_collaborative * collab_score) + (self.weight_content * content_score)
            hybrid_scores[item_id] = hybrid_score

        # 3. Trier par score
        sorted_items = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)
        top_items = sorted_items[:top_n]

        recommended_items = pd.DataFrame(top_items, columns=['item_id', 'hybrid_score'])
        if self.item_data is not None:
            recommended_items = recommended_items.merge(self.item_data, on='item_id', how='left')

        return recommended_items

    def recommend_similar_items(self, item_id, top_n=5):
        """
        Recommande des items similaires à un item donné en combinant les deux systèmes.

        Args:
            item_id: ID de l'item
            top_n: Nombre de recommandations à retourner

        Returns:
            DataFrame avec les items recommandés et leur score hybride
        """
        # 1. Recommandations par contenu
        content_recs = self.content_recommender.recommend(item_id, top_n=top_n*2)
        
        # 2. Recommandations par filtrage collaboratif (item-based ou SVD)
        collab_recs = self.collaborative_recommender.recommend_similar_items(item_id, top_n=top_n*2)

        hybrid_scores = {}

        # 3. Fusionner les deux
        for _, row in content_recs.iterrows():
            candidate_id = row['item_id']
            content_score = row.get('similarity', 1.0)

            # Vérifie si cet item existe aussi dans collab
            collab_score_row = collab_recs[collab_recs['item_id'] == candidate_id]
            if not collab_score_row.empty:
                collab_score = collab_score_row.iloc[0].get('score', 1.0)
            else:
                collab_score = 0

            hybrid_score = (self.weight_content * content_score) + (self.weight_collaborative * collab_score)
            hybrid_scores[candidate_id] = hybrid_score

        # 4. Trier par score
        sorted_items = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)
        top_items = sorted_items[:top_n]

        recommended_items = pd.DataFrame(top_items, columns=['item_id', 'hybrid_score'])
        if self.item_data is not None:
            recommended_items = recommended_items.merge(self.item_data, on='item_id', how='left')

        return recommended_items

    def evaluate(self, user_test_df, top_n=10):
        """
        Évalue les performances de l'hybride sur un ensemble d'utilisateurs de test.

        Args:
            user_test_df: DataFrame avec colonnes ['user_id', 'item_id']
            top_n: Nombre de recommandations à considérer

        Returns:
            Dictionnaire de métriques (ex: précision)
        """
        hits = 0
        total = len(user_test_df)

        for _, row in user_test_df.iterrows():
            user_id = row['user_id']
            true_item_id = row['item_id']

            recommendations = self.recommend_for_user(user_id, top_n=top_n)
            recommended_item_ids = recommendations['item_id'].tolist()

            if true_item_id in recommended_item_ids:
                hits += 1

        precision_at_k = hits / total if total > 0 else 0.0

        return {
            'precision_at_{}'.format(top_n): precision_at_k,
            'hits': hits,
            'total': total
        }
