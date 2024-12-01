from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('', include('users.urls')),
    # Эндпоинт для получения токена
    path('api/token/', obtain_auth_token, name='token_obtain'),
]
