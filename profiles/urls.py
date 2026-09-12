from django.urls import path
from . import views

"""
URL patterns for user authentication
and profile management.
"""
urlpatterns = [
    path(
        'activate/<uidb64>/<token>/',
        views.activate_account,
        name='activate_account'
    ),
    path('', views.profile, name='profile'),
    path(
        'order_history/<order_number>/',
        views.order_history,
        name='order_history'
    ),
    path('password_change/', views.password_change, name='password_change'),
    path('delete/', views.delete_account, name='delete_account'),
    path(
        'resend_verification/',
        views.resend_verification,
        name='resend_verification'
    ),
]
