from django.urls import path
from .views import (UserRecommendView, 
                    ItemRecommendView, 
                    RegisterView, 
                    LoginView, 
                    UserProfileView,
                    UserRecommendView
                )
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="API Recommandation",
      default_version='v1',
      description="API pour le système de recommandation de films/livres",
      contact=openapi.Contact(email="camara13fs@gmail.com"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path('recommend/user/', UserRecommendView.as_view(), name='recommend-user'),
    path('recommend/item/', ItemRecommendView.as_view(), name='recommend-item'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='profile'),

    # Docs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]# backend/recommandation_api/urls.py

"""
Mossoko
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ2NTM1NzQwLCJpYXQiOjE3NDY1MzExNzksImp0aSI6ImYwOGEwMjY3MjFkZDQ1ZTU4ODgxMTRiOTNkYjBhMzlmIiwidXNlcl9pZCI6MSwidXNlcm5hbWUiOiJNb3Nzb2tvIn0.nlbIv3uNVjUNoAI8HrGbnFiIy2_aUZpG_iZzrJATHUY",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc0NzEzNjk0MCwiaWF0IjoxNzQ2NTMyMTQwLCJqdGkiOiIxZjg5NTYyZjVkYmM0YzFjYWNjNTFmODNjMmNjNzJiMiIsInVzZXJfaWQiOjEsInVzZXJuYW1lIjoiTW9zc29rbyJ9.Cgm7HW00MKivb_6SnJp7xxYmixQnrjaYNr3gW8RgK9Q"
}
"""