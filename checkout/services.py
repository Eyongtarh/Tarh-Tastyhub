from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.shortcuts import get_object_or_404
from dishes.models import DishPortion
from .models import Order, OrderLineItem
import json
import logging

logger = logging.getLogger(__name__)


class OrderServiceError(Exception):
    """
    Custom exception for OrderService errors.
    """
    pass


class OrderService:
    """
    Service class to create orders and line items from a bag.
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
            line_total = (
                (portion.price * qty)
                .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            )
            subtotal += line_total
            items.append({
                "portion": portion,
                "quantity": qty,
                "price": portion.price,
                "line_total": line_total,
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
        subtotal, items = OrderService._compute_total_from_bag(bag)
        delivery_fee = (
            Decimal(form_data.get("delivery_fee", "0.00"))
            .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        )
        delivery_type = form_data.get("delivery_type", "delivery")
        pickup_time = form_data.get("pickup_time")
        if delivery_type == "pickup":
            delivery_fee = Decimal("0.00")
        grand_total = (
            (subtotal + delivery_fee)
            .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        )
        order = Order(
            user_profile=getattr(user, "userprofile", None),
            full_name=form_data.get("full_name", ""),
            email=form_data.get("email", ""),
            phone_number=form_data.get("phone_number", ""),
            street_address1=form_data.get("street_address1", ""),
            street_address2=form_data.get("street_address2", ""),
            town_or_city=form_data.get("town_or_city", ""),
            county=form_data.get("county", ""),
            postcode=form_data.get("postcode", ""),
            local=form_data.get("local", ""),
            delivery_type=delivery_type,
            pickup_time=pickup_time or None,
            stripe_pid=stripe_pid,
            order_total=subtotal,
            delivery_fee=delivery_fee,
            grand_total=grand_total,
        )
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
            f"subtotal={subtotal} delivery={delivery_fee} "
            f"grand_total={grand_total}"
        )

        return order
