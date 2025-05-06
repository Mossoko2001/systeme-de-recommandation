from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'profile_picture', 'favorite_genres')

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'profile_picture', 'favorite_genres')
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            profile_picture=validated_data.get('profile_picture'),
            favorite_genres=validated_data.get('favorite_genres')
        )
        return user


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
    # user_id = serializers.IntegerField()
    dataset_type = serializers.ChoiceField(choices=['books', 'movies'])
    top_n = serializers.IntegerField(required=False, default=5)
    # weight_content = serializers.FloatField(required=False, default=0.5)
    # weight_collaborative = serializers.FloatField(required=False, default=0.5)

class ItemRecommendParamsSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    dataset_type = serializers.ChoiceField(choices=['books', 'movies'])
    top_n = serializers.IntegerField(required=False, default=5)
    # weight_content = serializers.FloatField(required=False, default=0.5)
    # weight_collaborative = serializers.FloatField(required=False, default=0.5)