from rest_framework import serializers

class RecommendMovieSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    hybrid_score = serializers.FloatField()
    title = serializers.CharField()
    genres = serializers.CharField()

class RecommendBookSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    hybrid_score = serializers.FloatField()
    authors = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    genres = serializers.CharField()
    small_image_url = serializers.URLField()

class UserRecommendParamsSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    dataset_type = serializers.ChoiceField(choices=['books', 'movies'])
    top_n = serializers.IntegerField(required=False, default=5)
    weight_content = serializers.FloatField(required=False, default=0.5)
    weight_collaborative = serializers.FloatField(required=False, default=0.5)

class ItemRecommendParamsSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    dataset_type = serializers.ChoiceField(choices=['books', 'movies'])
    top_n = serializers.IntegerField(required=False, default=5)
    weight_content = serializers.FloatField(required=False, default=0.5)
    weight_collaborative = serializers.FloatField(required=False, default=0.5)