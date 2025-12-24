from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.shortcuts import get_object_or_404
from dishes.models import DishPortion
from .models import Order, OrderLineItem
import json
import logging

logger = logging.getLogger(__name__)


class OrderServiceError(Exception):
    pass


class OrderService:
    """
    Service class responsible for creating orders and order line items
    from a shopping bag.
    """

    @staticmethod
    def _compute_total_from_bag(bag):
        subtotal = Decimal("0.00")
        items = []

        for pid_str, qty in bag.items():
            try:
                pid = int(pid_str)
                qty = int(qty)
                if qty < 1:
                    continue
            except Exception:
                continue

            portion = get_object_or_404(DishPortion, pk=pid)
            line_total = (portion.price * qty).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            subtotal += line_total

            items.append({
                "portion": portion,
                "quantity": qty,
                "price": portion.price,
            })

        return subtotal, items

    @staticmethod
    @transaction.atomic
    def create_order_from_bag(
        user,
        bag,
        form_data,
        save_original_bag=True,
        stripe_pid=None,
    ):
        if not isinstance(bag, dict) or not bag:
            raise OrderServiceError("Bag is empty or invalid.")

        order_total, items = OrderService._compute_total_from_bag(bag)

        try:
            delivery_fee = Decimal(form_data.get("delivery_fee", "0.00"))
        except Exception:
            delivery_fee = Decimal("0.00")

        delivery_fee = delivery_fee.quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        grand_total = (order_total + delivery_fee).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        order = Order()
        order.user_profile = getattr(user, "userprofile", None)
        order.full_name = form_data.get("full_name", "")
        order.email = form_data.get("email", "")
        order.phone_number = form_data.get("phone_number", "")
        order.street_address1 = form_data.get("street_address1", "")
        order.street_address2 = form_data.get("street_address2", "")
        order.town_or_city = form_data.get("town_or_city", "")
        order.county = form_data.get("county", "")
        order.postcode = form_data.get("postcode", "")
        order.local = form_data.get("local", "")
        order.delivery_type = form_data.get("delivery_type", "delivery")
        order.pickup_time = form_data.get("pickup_time") or None
        order.stripe_pid = stripe_pid

        order.order_total = order_total
        order.delivery_fee = delivery_fee
        order.grand_total = grand_total

        if save_original_bag:
            try:
                order.original_bag = json.dumps(bag)
            except Exception:
                order.original_bag = None

        order.save()

        for it in items:
            OrderLineItem.objects.create(
                order=order,
                portion=it["portion"],
                quantity=it["quantity"],
                price=it["price"],
            )

        logger.info(
            f"OrderService: created order {order.order_number} "
            f"subtotal={order_total} delivery={delivery_fee} "
            f"grand_total={grand_total}"
        )

        return order
