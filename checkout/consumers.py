import json
import re
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import Order

logger = logging.getLogger(__name__)


def _safe_group_name(order_number):
    """
    Prevent Redis errors by removing any illegal characters.
    """
    cleaned = re.sub(r"[^A-Za-z0-9_\-]", "_", str(order_number))
    return f"order_{cleaned}"


class OrderTrackingConsumer(AsyncWebsocketConsumer):
    """
    Secure WebSocket consumer for real-time tracking of a specific order.
    Ensures:  
      - Only owner OR staff OR public-tracking users may join.
      - Prevents group injection.
      - Minimises DB hits by early rejection.
    """

    async def connect(self):
        order_number = self.scope["url_route"]["kwargs"].get("order_number")

        if not order_number:
            await self.close()
            return

        self.order_group_name = _safe_group_name(order_number)

        user = self.scope.get("user")

        if not user or not user.is_authenticated:
            await self.close()
            return

        order = await self._get_order(order_number)
        if not order:
            await self.close()
            return

        owner_user = getattr(order.user_profile, "user", None) if order.user_profile else None
        is_owner = owner_user == user
        is_staff = user.is_staff
        is_public = order.public_tracking

        if is_owner or is_staff or is_public:
            await self.channel_layer.group_add(self.order_group_name, self.channel_name)
            await self.accept()
        else:
            logger.warning(
                f"Unauthorized WS access attempt: order={order_number}, user={user.username}"
            )
            await self.close()

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.order_group_name, self.channel_name)
        except Exception as e:
            logger.warning(f"WebSocket disconnect error: {e}")

    async def order_update(self, event):
        """
        Broadcast order status updates.
        """
        try:
            await self.send(text_data=json.dumps({
                "status": event.get("status"),
                "progress": event.get("progress", 0),
                "timestamp": event.get("timestamp")
            }))
        except Exception as e:
            logger.error(f"Failed to send order update WS message: {e}")

    @database_sync_to_async
    def _get_order(self, order_number):
        try:
            return Order.objects.select_related("user_profile", "user_profile__user").get(
                order_number=order_number
            )
        except Order.DoesNotExist:
            return None


class AdminOrderConsumer(AsyncWebsocketConsumer):
    """
    WebSocket channel for staff dashboard live updates.
    Only staff users may join.
    """

    async def connect(self):
        user = self.scope.get("user", None)

        if not user or not user.is_staff:
            await self.close()
            return

        self.admin_group_name = "admin_orders"

        await self.channel_layer.group_add(self.admin_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.admin_group_name, self.channel_name)
        except Exception as e:
            logger.warning(f"Admin WS disconnect error: {e}")

    async def order_update(self, event):
        """
        Broadcast to staff dashboards.
        """
        try:
            await self.send(text_data=json.dumps(event))
        except Exception as e:
            logger.error(f"Failed to send admin WS update: {e}")
