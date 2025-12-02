from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate_account'),
    path('resend-verification/', views.resend_verification_email, name='resend_verification'),
    path('', views.profile, name='profile'),
    path('order_history/<order_number>/', views.order_history, name='order_history'),
    path('password_change/', views.password_change, name='password_change'),
    path('delete/', views.delete_account, name='delete_account'),
]
