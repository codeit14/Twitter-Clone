"""
twitter URL Configuration
"""
from django.urls import path, include

urlpatterns = [
    path('rest_auth/', include('rest_auth.urls')),
    path('tweets/', include('tweets.urls')),
]
