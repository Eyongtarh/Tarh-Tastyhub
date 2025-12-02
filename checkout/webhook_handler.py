import json
import logging
import uuid
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse
from django.template.loader import render_to_string

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Order, OrderLineItem
from dishes.models import DishPortion
from profiles.models import UserProfile

logger = logging.getLogger(__name__)


class StripeWH_Handler:
    """Handles Stripe webhooks."""

    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order, email_override=None):
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
            logger.exception(f"Email send failed for order {order.order_number}: {e}")

    def handle_event(self, event):
        logger.info(f"Unhandled webhook: {event.get('type')}")
        return HttpResponse("Unhandled event", status=200)

    def _parse_bag(self, bag_raw):
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

    def handle_payment_intent_succeeded(self, event):
        intent = event["data"]["object"]
        pid = intent.get("id")
        metadata = intent.get("metadata", {}) or {}

        bag_raw = metadata.get("bag", "{}")
        bag = self._parse_bag(bag_raw)

        try:
            charge = intent.get("charges", {}).get("data", [{}])[0]
            billing_email = charge.get("billing_details", {}).get("email")
        except Exception:
            billing_email = None

        email_meta = metadata.get("email")
        username = metadata.get("username", "AnonymousUser")
        save_info = str(metadata.get("save_info", "")).lower() in ["true", "1"]

        shipping = intent.get("shipping", {}) or {}
        addr = shipping.get("address", {}) or {}

        profile = None
        if username != "AnonymousUser":
            try:
                profile = UserProfile.objects.get(user__username=username)
            except UserProfile.DoesNotExist:
                profile = None

        try:
            existing = Order.objects.get(stripe_pid=pid)
            self._send_confirmation_email(existing)
            return HttpResponse("Order already exists", status=200)
        except Order.DoesNotExist:
            pass

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
                    local=(addr.get("country") or "").strip()[:80],
                    original_bag=bag_raw,
                    stripe_pid=pid,
                )

                running_total = Decimal("0.00")

                for portion_id, qty in bag.items():
                    try:
                        portion = DishPortion.objects.select_related("dish").get(pk=portion_id)
                    except DishPortion.DoesNotExist:
                        logger.warning(f"Missing portion id {portion_id}, skipping.")
                        continue

                    line_total = (portion.price * qty).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                    running_total += line_total

                    OrderLineItem.objects.create(
                        order=order,
                        portion=portion,
                        quantity=qty,
                        price=portion.price,
                    )

                order.grand_total = running_total
                order.save()

        except Exception as e:
            logger.exception(f"Order creation failed: {e}")
            return HttpResponse("Order error", status=500)

        self._send_confirmation_email(order)

        try:
            layer = get_channel_layer()
            async_to_sync(layer.group_send)(
                f"order_{order.order_number}",
                {
                    "type": "order_update",
                    "order_number": order.order_number,
                    "status": order.status,
                    "progress": 25,
                },
            )
        except Exception as e:
            logger.warning(f"WebSocket error: {e}")

        logger.info(f"Order created OK: {order.order_number}")
        return HttpResponse("Success", status=200)

    def handle_payment_intent_payment_failed(self, event):
        logger.info("Payment failed")
        return HttpResponse("Payment failed", status=200)
