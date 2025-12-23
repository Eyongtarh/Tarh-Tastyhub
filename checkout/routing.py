from django.urls import re_path
from . import consumers


"""
Defines WebSocket URL routes for real-time order tracking
and admin order update notifications.
"""
websocket_urlpatterns = [
    re_path(
        r'ws/order/(?P<order_number>[\w\-]+)/$',
        consumers.OrderTrackingConsumer.as_asgi(),
    ),
    re_path(
        r'ws/admin/$',
        consumers.AdminOrderConsumer.as_asgi(),
    ),
]
