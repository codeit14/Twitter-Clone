from django.urls import path
from .views import SignupView, LoginView, LogoutView, UserDetailsAPIView

urlpatterns = [
    path('signup/', SignupView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('user/<uuid:pk>/', UserDetailsAPIView.as_view()),
]
