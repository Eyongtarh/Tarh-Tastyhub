from django.urls import path
from . import views, order_tracking_view, admin_dashboard_view, views_webhook

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('track/<str:order_number>/', order_tracking_view.order_tracking, name='order_tracking'),
    path('admin-dashboard/', admin_dashboard_view.admin_dashboard, name='admin_dashboard'),
    path('update-status/<int:order_id>/', admin_dashboard_view.update_order_status, name='update_order_status'),
    path('webhook/', views_webhook.webhook, name='webhook'),
    path('success/<str:order_number>/', views.checkout_success, name='checkout_success'),
]
