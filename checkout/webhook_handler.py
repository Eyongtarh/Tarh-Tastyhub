import json
import logging
import uuid
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date, time

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse
from django.template.loader import render_to_string

import stripe

from .models import Order, OrderLineItem
from dishes.models import DishPortion
from profiles.models import UserProfile

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

# Delivery fee settings
MIN_FREE_DELIVERY = getattr(settings, "FREE_DELIVERY_THRESHOLD", Decimal("60.00"))
DEFAULT_DELIVERY = getattr(settings, "DEFAULT_DELIVERY_FEE", Decimal("4.00"))


def _to_decimal(value, fallback=Decimal("0.00")):
    try:
        if value in (None, ""):
            return fallback
        return Decimal(str(value)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    except Exception:
        return fallback


class StripeWH_Handler:
    """
    Handle Stripe webhooks.
    Orders are created ONLY after payment_intent.succeeded
    """

    def __init__(self, request):
        self.request = request

    # ---------------- EMAIL ---------------- #

    def _send_confirmation_email(self, order):
        if not order.email:
            logger.warning(f"No email for order {order.order_number}")
            return

        subject = render_to_string(
            "checkout/confirmation_emails/confirmation_email_subject.txt",
            {"order": order},
        ).strip()

        body = render_to_string(
            "checkout/confirmation_emails/confirmation_email_body.txt",
            {"order": order, "contact_email": settings.DEFAULT_FROM_EMAIL},
        )

        try:
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [order.email],
            )
        except Exception:
            logger.exception(f"Email failed for order {order.order_number}")

    # ---------------- HELPERS ---------------- #

    def _parse_bag(self, raw):
        try:
            data = json.loads(raw) if isinstance(raw, str) else raw
        except Exception:
            return {}

        if not isinstance(data, dict):
            return {}

        cleaned = {}
        for key, qty in data.items():
            try:
                cleaned[str(key)] = max(1, int(qty))
            except Exception:
                continue
        return cleaned

    def _parse_pickup_time(self, value):
        if not value:
            return None
        try:
            hour, minute = map(int, value.split(":"))
            return datetime.combine(date.today(), time(hour, minute))
        except Exception:
            return None

    # ---------------- DEFAULT ---------------- #

    def handle_event(self, event):
        logger.info(f"Unhandled Stripe event: {event['type']}")
        return HttpResponse(status=200)

    # ---------------- SUCCESS ---------------- #

    def handle_payment_intent_succeeded(self, event):
        intent = event["data"]["object"]
        pid = intent["id"]
        metadata = intent.get("metadata", {}) or {}

        # Idempotency: do not duplicate orders
        if Order.objects.filter(stripe_pid=pid).exists():
            logger.info(f"Order already exists for {pid}")
            return HttpResponse(status=200)

        bag = self._parse_bag(metadata.get("bag", "{}"))
        delivery_type = metadata.get("delivery_type", "delivery")
        pickup_time = self._parse_pickup_time(metadata.get("pickup_time"))
        email = metadata.get("email") or intent.get("receipt_email", "")
        username = metadata.get("username", "AnonymousUser")

        profile = None
        if username != "AnonymousUser":
            try:
                profile = UserProfile.objects.get(user__username=username)
            except UserProfile.DoesNotExist:
                pass

        # Billing details
        try:
            charge = intent["charges"]["data"][0]
            billing = charge.get("billing_details", {})
            address = billing.get("address", {}) or {}
        except Exception:
            billing = {}
            address = {}

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    order_number=uuid.uuid4().hex[:16].upper(),
                    user_profile=profile,
                    full_name=(billing.get("name") or "")[:50],
                    email=email[:254],
                    phone_number=(billing.get("phone") or "")[:20],
                    street_address1=(address.get("line1") or "")[:80],
                    street_address2=(address.get("line2") or "")[:80],
                    town_or_city=(address.get("city") or "")[:40],
                    county=(address.get("state") or "")[:80],
                    postcode=(address.get("postal_code") or "")[:20],
                    delivery_type=delivery_type,
                    pickup_time=pickup_time,
                    original_bag=json.dumps(bag),
                    stripe_pid=pid,
                )

                subtotal = Decimal("0.00")

                for portion_id, qty in bag.items():
                    try:
                        portion = DishPortion.objects.get(pk=int(portion_id))
                    except (DishPortion.DoesNotExist, ValueError):
                        continue

                    line_total = (portion.price * qty).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                    subtotal += line_total

                    OrderLineItem.objects.create(
                        order=order,
                        portion=portion,
                        quantity=qty,
                        price=portion.price,
                    )

                order.delivery_fee = (
                    Decimal("0.00")
                    if delivery_type == "pickup" or subtotal >= MIN_FREE_DELIVERY
                    else DEFAULT_DELIVERY
                )
                order.grand_total = _to_decimal(subtotal + order.delivery_fee)
                order.save()

        except Exception:
            logger.exception("Order creation failed")
            return HttpResponse(status=500)

        self._send_confirmation_email(order)
        logger.info(f"Order created: {order.order_number}")
        return HttpResponse(status=200)

    # ---------------- FAILED ---------------- #

    def handle_payment_intent_payment_failed(self, event):
        intent = event["data"]["object"]
        logger.warning(f"Payment failed: {intent.get('id')}")
        return HttpResponse(status=200)
