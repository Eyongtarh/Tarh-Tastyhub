"""
URL patterns for Feedback app.
(ubmitting feedback and marking feedback as handled/unhandled)
"""
from django.urls import path
from . import views


urlpatterns = [
    path('', views.feedback_view, name='feedback'),
    path('mark-handled/<int:pk>/', views.mark_handled, name='mark-handled'),
    path(
        'mark-unhandled/<int:pk>/',
        views.mark_unhandled,
        name='mark-unhandled'
    ),
]
