from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    UserRecommendParamsSerializer,
    ItemRecommendParamsSerializer,
    RecommendBookSerializer,
    RecommendMovieSerializer
)
from .services import build_hybrid_recommender

class UserRecommendView(APIView):
    """
    GET /api/recommend/user/?user_id=<id>&dataset_type=<books|movies>&top_n=<n>&weight_content=<w1>&weight_collaborative=<w2>
    """
    def get(self, request, format=None):
        params = UserRecommendParamsSerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        validated = params.validated_data

        hybrid_recommender = build_hybrid_recommender(
            dataset_type=validated['dataset_type'],
            weight_content=validated['weight_content'],
            weight_collaborative=validated['weight_collaborative']
        )

        df = hybrid_recommender.recommend_for_user(
            user_id=validated['user_id'],
            top_n=validated['top_n']
        )
        data = df.to_dict(orient='records')
        if validated['dataset_type'] == 'books':
            serializer = RecommendBookSerializer(data, many=True)
        else:
            serializer = RecommendMovieSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ItemRecommendView(APIView):
    """
    GET /api/recommend/item/?item_id=<id>&dataset_type=<books|movies>&top_n=<n>&weight_content=<w1>&weight_collaborative=<w2>
    """
    def get(self, request, format=None):
        params = ItemRecommendParamsSerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        validated = params.validated_data

        hybrid_recommender = build_hybrid_recommender(
            dataset_type=validated['dataset_type'],
            weight_content=validated['weight_content'],
            weight_collaborative=validated['weight_collaborative']
        )

        df = hybrid_recommender.recommend_similar_items(
            item_id=validated['item_id'],
            top_n=validated['top_n']
        )
        data = df.to_dict(orient='records')
        if validated['dataset_type'] == 'books':
            serializer = RecommendBookSerializer(data, many=True)
        else:
            serializer = RecommendMovieSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
