from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/order/(?P<order_number>[\w\-]+)/$', consumers.OrderTrackingConsumer.as_asgi()),
    re_path(r'ws/admin/$', consumers.AdminOrderConsumer.as_asgi()),
]
