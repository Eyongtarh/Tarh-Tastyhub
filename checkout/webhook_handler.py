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

from .models import Order, OrderLineItem
from dishes.models import DishPortion
from profiles.models import UserProfile

logger = logging.getLogger(__name__)

# Delivery fee settings
MIN_FREE_DELIVERY = getattr(settings, "FREE_DELIVERY_THRESHOLD", Decimal("60.00"))
DEFAULT_DELIVERY = getattr(settings, "DEFAULT_DELIVERY_FEE", Decimal("4.00"))


def _to_decimal(value, fallback=Decimal("0.00")):
    """Safely convert a value to a Decimal rounded to two decimal places."""
    try:
        if value is None or value == "":
            return fallback
        if isinstance(value, Decimal):
            return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except Exception:
        return fallback


class StripeWH_Handler:
    """Handles Stripe webhooks for successful or failed payments."""

    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order, email_override=None):
        """Send an order confirmation email to the customer."""
        email = (
            email_override
            or order.email
            or getattr(getattr(order.user_profile, "user", None), "email", None)
        )
        if not email:
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
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email])
        except Exception as e:
            logger.exception(
                f"Email send failed for order {order.order_number}: {e}"
            )

    def handle_event(self, event):
        """Default handler for unrecognized Stripe events."""
        logger.info(f"Unhandled webhook: {event.get('type')}")
        return HttpResponse("Unhandled event", status=200)

    def _parse_bag(self, bag_raw):
        """Parse and clean bag data from Stripe metadata."""
        try:
            data = json.loads(bag_raw) if isinstance(bag_raw, str) else bag_raw
        except Exception:
            logger.exception("Could not decode bag JSON")
            return {}

        if not isinstance(data, dict):
            return {}

        cleaned = {}
        for pid, qty in data.items():
            try:
                cleaned[str(pid)] = max(1, int(qty))
            except Exception:
                logger.warning(f"Invalid bag entry: {pid}:{qty}")
        return cleaned

    def _parse_pickup_time(self, pickup_time_str):
        """Convert pickup_time string 'HH:MM' into a datetime object for today."""
        if not pickup_time_str:
            return None
        try:
            hour, minute = map(int, pickup_time_str.split(":"))
            return datetime.combine(date.today(), time(hour=hour, minute=minute))
        except Exception:
            logger.warning(f"Invalid pickup_time format: {pickup_time_str}")
            return None

    def handle_payment_intent_succeeded(self, event):
        """Handle successful Stripe payment intents by creating the corresponding Order."""
        intent = event["data"]["object"]
        pid = intent.get("id")
        metadata = intent.get("metadata", {}) or {}

        bag_raw = metadata.get("bag", "{}")
        bag = self._parse_bag(bag_raw)

        # Billing email
        try:
            charge = intent.get("charges", {}).get("data", [{}])[0]
            billing_email = charge.get("billing_details", {}).get("email")
        except Exception:
            billing_email = None

        email_meta = metadata.get("email")
        username = metadata.get("username", "AnonymousUser")

        shipping = intent.get("shipping", {}) or {}
        addr = shipping.get("address", {}) or {}

        profile = None
        if username != "AnonymousUser":
            try:
                profile = UserProfile.objects.get(user__username=username)
            except UserProfile.DoesNotExist:
                profile = None

        delivery_type = metadata.get("delivery_type", "delivery")
        pickup_time = self._parse_pickup_time(metadata.get("pickup_time"))
        local = metadata.get("local", "")

        # Check for existing order
        if Order.objects.filter(stripe_pid=pid).exists():
            existing = Order.objects.get(stripe_pid=pid)
            self._send_confirmation_email(existing)
            return HttpResponse("Order already exists", status=200)

        # Create order in a transaction
        try:
            with transaction.atomic():
                order_number = uuid.uuid4().hex[:16].upper()
                order = Order.objects.create(
                    order_number=order_number,
                    user_profile=profile,
                    full_name=(shipping.get("name") or "").strip()[:50],
                    email=(email_meta or billing_email or "").strip()[:254],
                    phone_number=(shipping.get("phone") or "").strip()[:20],
                    street_address1=(addr.get("line1") or "").strip()[:80],
                    street_address2=(addr.get("line2") or "").strip()[:80],
                    town_or_city=(addr.get("city") or "").strip()[:40],
                    county=(addr.get("state") or "").strip()[:80],
                    postcode=(addr.get("postal_code") or "").strip()[:20],
                    local=local,
                    delivery_type=delivery_type,
                    pickup_time=pickup_time,
                    original_bag=bag_raw,
                    stripe_pid=pid,
                )

                running_total = Decimal("0.00")
                for portion_id, qty in bag.items():
                    try:
                        portion = DishPortion.objects.select_related("dish").get(
                            pk=int(portion_id)
                        )
                    except (DishPortion.DoesNotExist, ValueError):
                        logger.warning(
                            f"Missing or invalid portion id {portion_id}, skipping."
                        )
                        continue

                    line_total = (
                        portion.price
                        * int(qty)
                    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    running_total += line_total

                    OrderLineItem.objects.create(
                        order=order,
                        portion=portion,
                        quantity=int(qty),
                        price=portion.price,
                    )

                # Delivery fee
                order.delivery_fee = _to_decimal(
                    0.00 if running_total >= MIN_FREE_DELIVERY else DEFAULT_DELIVERY
                )
                order.grand_total = _to_decimal(running_total + order.delivery_fee)

                order.save()

        except Exception as e:
            logger.exception(f"Order creation failed: {e}")
            return HttpResponse("Order error", status=500)

        self._send_confirmation_email(order)
        logger.info(f"Order created OK: {order.order_number}")
        return HttpResponse("Success", status=200)

    def handle_payment_intent_payment_failed(self, event):
        """Handle failed Stripe payment intents."""
        intent = event["data"]["object"]
        pid = intent.get("id")
        metadata = event.get("metadata", {}) or {}

        try:
            logger.info(
                "Payment failed for pid=%s metadata=%s", pid, json.dumps(metadata)
            )
        except Exception:
            logger.info("Payment failed (could not dump metadata)")

        return HttpResponse("Payment failed", status=200)
