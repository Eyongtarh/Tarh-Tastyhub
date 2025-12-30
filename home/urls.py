"""
URL patterns for index.html pages.
(home, privacy policy, and terms & conditions pages)
"""
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('privacy/', views.privacy_policy, name='privacy'),
    path('terms/', views.terms_and_conditions, name='terms'),
]
