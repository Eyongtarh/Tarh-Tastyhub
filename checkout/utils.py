import logging
from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.utils import timezone
from dishes.models import Dish, DishPortion
from .models import Order, OrderLineItem

logger = logging.getLogger(__name__)


def validate_bag(bag):
    """
    Validate bag structure and contents.
    Expect bag as {dish_portion_id: quantity}
    """
    if not isinstance(bag, dict):
        raise ValidationError("Bag must be a dictionary.")

    for portion_id, quantity in bag.items():
        if not isinstance(quantity, int) or quantity < 1:
            raise ValidationError(f"Invalid quantity for portion {portion_id}")
        if not DishPortion.objects.filter(id=portion_id).exists():
            raise ValidationError(f"Dish portion with ID {portion_id} does not exist.")


@transaction.atomic
def create_order_from_bag(user, bag, form_data):
    """
    Create an order and line items from bag/session using DishPortion.
    """
    validate_bag(bag)

    order = Order()
    order.user_profile = getattr(user, 'userprofile', None)
    order.full_name = form_data.get('full_name')
    order.email = form_data.get('email')
    order.phone_number = form_data.get('phone_number')
    order.street_address1 = form_data.get('street_address1')
    order.street_address2 = form_data.get('street_address2')
    order.town_or_city = form_data.get('town_or_city')
    order.county = form_data.get('county')
    order.postcode = form_data.get('postcode')
    order.local = form_data.get('local')
    order.save()

    for portion_id, quantity in bag.items():
        portion = get_object_or_404(DishPortion, pk=portion_id)
        line_item = OrderLineItem(
            order=order,
            dish=portion.dish,
            portion=portion,
            quantity=quantity,
            lineitem_total=portion.price * quantity
        )
        line_item.save()

    logger.info(f"Order {order.order_number} created for user {user}")
    return order


def calculate_bag_total(bag):
    """
    Calculate total price for a bag with DishPortions.
    """
    total = Decimal("0.00")
    for portion_id, quantity in bag.items():
        portion = get_object_or_404(DishPortion, pk=portion_id)
        total += portion.price * quantity
    return total


def prevent_order_spam(request, key='last_order_time', cooldown_seconds=30):
    """
    Prevent repeated order submissions in a short time.
    """
    now = timezone.now()
    last_time = request.session.get(key)

    if last_time:
        elapsed = (now - last_time).total_seconds()
        if elapsed < cooldown_seconds:
            raise ValidationError(f"Please wait {int(cooldown_seconds - elapsed)} seconds before placing another order.")

    request.session[key] = now
    request.session.modified = True
