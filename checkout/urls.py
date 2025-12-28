from django.urls import path
from . import views
from . import order_tracking_view
from . import admin_dashboard_view
from . import views_webhook

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('track/<str:order_number>/',
         order_tracking_view.order_tracking,
         name='order_tracking'),
    path('admin-dashboard/',
         admin_dashboard_view.admin_dashboard,
         name='admin_dashboard'),
    path('update-status/<int:order_id>/',
         admin_dashboard_view.update_order_status,
         name='update_order_status'),
    path('webhook/', views_webhook.webhook, name='webhook'),
    path('success/<str:order_number>/',
         views.checkout_success,
         name='checkout_success'),
    path(
        'feedback/mark-handled/<int:feedback_id>/',
        admin_dashboard_view.mark_feedback_handled,
        name='mark_feedback_handled'
    ),
    path(
        'feedback/mark-unhandled/<int:feedback_id>/',
        admin_dashboard_view.mark_feedback_unhandled,
        name='mark_feedback_unhandled'
    ),
    path(
        'cancel-order/<int:order_id>/',
        admin_dashboard_view.cancel_order,
        name='cancel_order'
     ),
    path(
        'cache_checkout_data/',
        views.cache_checkout_data,
        name='cache_checkout_data'),
]
