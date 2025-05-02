from django.urls import path
from .views import UserRecommendView, ItemRecommendView

urlpatterns = [
    path('recommend/user/', UserRecommendView.as_view(), name='recommend-user'),
    path('recommend/item/', ItemRecommendView.as_view(), name='recommend-item'),
]# backend/recommandation_api/urls.py