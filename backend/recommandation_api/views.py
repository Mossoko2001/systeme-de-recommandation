from rest_framework import generics, permissions, status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (
    UserRecommendParamsSerializer,
    ItemRecommendParamsSerializer,
    RecommendBookSerializer,
    RecommendMovieSerializer,
    UserSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
)
from .services import build_hybrid_recommender
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()
class RegisterView(generics.CreateAPIView):
    """
    Endpoint d'inscription des utilisateurs.
    Crée un nouveau compte avec username/email/password.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Inscription d'un nouvel utilisateur",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response('Utilisateur créé', RegisterSerializer),
            400: "Données invalides"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class LoginView(TokenObtainPairView):
    """
    POST: Endpoint de Connexion d'un utilisateur.
    POST api/login/?username=nomUtilisateur&password=motdepass
    """
    serializer_class = CustomTokenObtainPairSerializer
    @swagger_auto_schema(
        request_body=CustomTokenObtainPairSerializer,
        responses={
            200: openapi.Response("Utilisateur connecté", CustomTokenObtainPairSerializer),
            400: openapi.Response("L'utilisateur n'existe pas.")
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class UserProfileView(generics.RetrieveAPIView):
    """
    GET: Récupérer le profil de l'utilisateur connecté.
    Nécessite une authentification JWT valide.
    GET api/profile
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Récupérer le profil de l'utilisateur",
        responses={
            200: openapi.Response('Profil utilisateur', UserSerializer),
            401: "Token invalide/expiré"
        }
    )
    
    def get_object(self):
        return self.request.user


class UserRecommendView(APIView):
    """
    GET: Liste des recommandations personnalisées pour l'utilisateur connecter
    Nécessite une authentification JWT valide.

    GET /api/recommend/user/?&dataset_type=<books|movies>&top_n=<n>
    """
    permission_classes = [permissions.IsAuthenticated] # Assurez-vous que l'utilisateur est authentifié

    @swagger_auto_schema(
        operation_description="Recommandations personnalisées pour l'utilisateur",
        manual_parameters=[
            openapi.Parameter(
                'dataset_type',
                openapi.IN_QUERY,
                description="Type de données (books/movies)",
                type=openapi.TYPE_STRING,
                enum=['books', 'movies']
            ),
            openapi.Parameter(
                'top_n',
                openapi.IN_QUERY,
                description="Nombre de recommandation à retourner",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="JWT Token (Bearer {token})",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: "Liste des recommandations",
            401: "Token invalide/expiré"
        }
    )

    def get(self, request, format=None):
        params = UserRecommendParamsSerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        validated = params.validated_data

        # Utilisez l'ID de l'utilisateur connecté
        user_id = request.user.id
        weight_content = 0.3
        weight_collaborative = 0.7

        hybrid_recommender = build_hybrid_recommender(
            dataset_type=validated['dataset_type'],
            weight_content=weight_content,
            weight_collaborative=weight_collaborative
        )

        df = hybrid_recommender.recommend_for_user(
            # user_id=validated['user_id'],
            user_id=user_id,
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

    @swagger_auto_schema(
        operation_description="Recommandations personnalisées pour l'utilisateur",
        manual_parameters=[
            openapi.Parameter(
                'item_id',
                openapi.IN_QUERY,
                description="Identifiant de Item",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                'dataset_type',
                openapi.IN_QUERY,
                description="Type de données (books/movies)",
                type=openapi.TYPE_STRING,
                enum=['books', 'movies']
            ),
            openapi.Parameter(
                'top_n',
                openapi.IN_QUERY,
                description="Nombre de recommandation à retourner",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="JWT Token (Bearer {token})",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: "Liste des recommandations",
            401: "Token invalide/expiré"
        }
    )

    def get(self, request, format=None):
        params = ItemRecommendParamsSerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        validated = params.validated_data

        hybrid_recommender = build_hybrid_recommender(
            dataset_type=validated['dataset_type'],
            # weight_content=validated['weight_content'],
            # weight_collaborative=validated['weight_collaborative']
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
    
