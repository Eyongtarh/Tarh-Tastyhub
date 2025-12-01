from decimal import Decimal
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
    @staticmethod
    def _compute_total_from_bag(bag):
        """
        bag: { portion_id (str or int): quantity (int) }
        """
        total = Decimal('0.00')
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
            line_total = portion.price * qty
            total += line_total
            items.append({
                'portion': portion,
                'quantity': qty,
                'price': portion.price,
                'line_total': line_total
            })
        return total, items

    @staticmethod
    @transaction.atomic
    def create_order_from_bag(user, bag, form_data, save_original_bag=True, stripe_pid=None):
        """
        Create Order + OrderLineItems from bag
        bag: { portion_id: quantity }
        form_data: dict-like with customer & address fields (keys match Order fields)
        Returns created Order
        """
        if not isinstance(bag, dict) or len(bag) == 0:
            raise OrderServiceError("Bag is empty or invalid.")

        # compute totals and items
        grand_total, items = OrderService._compute_total_from_bag(bag)

        # create order
        order = Order()
        order.user_profile = getattr(user, 'userprofile', None)
        order.full_name = form_data.get('full_name') or form_data.get('name') or ''
        order.email = form_data.get('email') or ''
        order.phone_number = form_data.get('phone_number') or ''
        order.street_address1 = form_data.get('street_address1') or ''
        order.street_address2 = form_data.get('street_address2') or ''
        order.town_or_city = form_data.get('town_or_city') or ''
        order.county = form_data.get('county') or ''
        order.postcode = form_data.get('postcode') or ''
        order.local = form_data.get('local') or ''
        order.delivery_type = form_data.get('delivery_type') or 'delivery'
        if form_data.get('pickup_time'):
            order.pickup_time = form_data.get('pickup_time')
        order.stripe_pid = stripe_pid or None

        # assign grand total BEFORE saving lineitems
        order.grand_total = grand_total

        # Optionally attach original bag as JSON
        try:
            if save_original_bag:
                order.original_bag = json.dumps(bag)
        except Exception:
            order.original_bag = None

        order.save()

        # Create line items
        for it in items:
            OrderLineItem.objects.create(
                order=order,
                portion=it['portion'],
                quantity=it['quantity'],
                price=it['price']
            )

        # Return created object
        logger.info(f"OrderService: created order {order.order_number} total {order.grand_total}")
        return order
