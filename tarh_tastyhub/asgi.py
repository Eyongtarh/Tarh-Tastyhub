"""
ASGI config for tarh_tastyhub project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import checkout.routing as checkout_routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tarh_tastyhub.settings')

django_asgi_app = get_asgi_application()

websocket_urlpatterns = []
try:
    import notifications.routing as notifications_routing
    websocket_urlpatterns = checkout_routing.websocket_urlpatterns + notifications_routing.websocket_urlpatterns
except Exception:
    websocket_urlpatterns = checkout_routing.websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
