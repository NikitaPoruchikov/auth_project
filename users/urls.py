from django.urls import path

from .views import (RegisterView, SendCodeView, VerifyCodeView,
                    LoginView, ProfileView, ActivateInviteView)

urlpatterns = [
    path('register/', RegisterView.as_view(),
         name='register'),
    path('send_code/', SendCodeView.as_view(),
         name='send_code'),
    path('verify_code/', VerifyCodeView.as_view(),
         name='verify_code'),
    path('login/', LoginView.as_view(),
         name='login'),
    path('profile/', ProfileView.as_view(),
         name='profile'),
    path('activate_invite/', ActivateInviteView.as_view(),
         name='activate_invite'),
]
