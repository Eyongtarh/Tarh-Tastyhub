from decimal import Decimal, ROUND_HALF_UP
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods, require_POST

import stripe

from .forms import OrderForm
from .services import OrderService, OrderServiceError
from .models import Order

logger = logging.getLogger(__name__)

stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", None)


def _to_decimal(value, fallback=Decimal("0.00")):
    try:
        if isinstance(value, Decimal):
            return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except Exception:
        return fallback


@require_http_methods(["GET", "POST"])
def checkout(request):
    from bag.context_processors import bag_contents

    ctx = bag_contents(request) or {}
    bag_items = ctx.get("bag_items") or ctx.get("items") or []
    bag = request.session.get("bag", {}) or {}

    if not bag:
        messages.error(request, "Your bag is empty. Add items before checkout.")
        return redirect("bag")

    subtotal = _to_decimal(ctx.get("bag_total") or Decimal("0.00"))

    try:
        MIN_FREE = _to_decimal(getattr(settings, "MIN_FREE_DELIVERY", Decimal("80.00")))
        DEFAULT_DELIVERY = _to_decimal(getattr(settings, "DEFAULT_DELIVERY_FEE", Decimal("4.00")))
    except Exception:
        MIN_FREE = Decimal("80.00")
        DEFAULT_DELIVERY = Decimal("4.00")

    delivery_fee = DEFAULT_DELIVERY if subtotal < MIN_FREE else Decimal("0.00")
    grand_total = (subtotal + delivery_fee).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    delivery_fee_display = f"${delivery_fee:.2f}" if delivery_fee > 0 else "Free"

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            try:
                stripe_pid = request.POST.get("stripe_pid")

                if stripe_pid and Order.objects.filter(stripe_pid=stripe_pid).exists():
                    existing = Order.objects.get(stripe_pid=stripe_pid)
                    messages.info(request, "Order already processed.")
                    return redirect("checkout_success", order_number=existing.order_number)

                form_data = form.cleaned_data.copy()
                form_data["delivery_fee"] = str(delivery_fee)

                order = OrderService.create_order_from_bag(
                    user=request.user if request.user.is_authenticated else None,
                    bag=bag,
                    form_data=form_data,
                    save_original_bag=True,
                    stripe_pid=stripe_pid,
                )

                request.session["bag"] = {}
                request.session.modified = True

                messages.success(
                    request,
                    '<span class="fa-icon"><i class="fa-solid fa-check"></i></span> Order placed successfully!',
                    extra_tags="safe",
                )
                return redirect("checkout_success", order_number=order.order_number)

            except OrderServiceError as e:
                logger.exception("OrderServiceError during checkout")
                messages.error(request, str(e))
            except Exception as e:
                logger.exception("Unexpected error during checkout: %s", e)
                messages.error(request, "Error processing your order. Please contact support.")
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        initial = {}
        if request.user.is_authenticated:
            profile = getattr(request.user, "userprofile", None)
            initial = {
                "full_name": request.user.get_full_name() or request.user.username,
                "email": request.user.email,
                "phone_number": getattr(profile, "default_phone_number", ""),
                "street_address1": getattr(profile, "default_street_address1", ""),
                "street_address2": getattr(profile, "default_street_address2", ""),
                "town_or_city": getattr(profile, "default_town_or_city", ""),
                "county": getattr(profile, "default_county", ""),
                "postcode": getattr(profile, "default_postcode", ""),
                "local": getattr(profile, "default_local", ""),
            }
        form = OrderForm(initial=initial)

    client_secret = None
    try:
        amount_cents = int((grand_total * 100).to_integral_value(rounding=ROUND_HALF_UP))
        currency = getattr(settings, "STRIPE_CURRENCY", "usd")

        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=currency,
            automatic_payment_methods={"enabled": True},
            metadata={
                "delivery_fee": str(delivery_fee),
            },
        )

        client_secret = intent.client_secret
    except Exception as e:
        logger.exception("Failed to create Stripe PaymentIntent: %s", e)

    stripe_public_key = getattr(settings, "STRIPE_PUBLIC_KEY", "")

    template_ctx = {
        "form": form,
        "stripe_public_key": stripe_public_key,
        "client_secret": client_secret,
        "bag_items": bag_items,
        "bag_total": subtotal,
        "delivery_fee": delivery_fee,
        "delivery_fee_display": delivery_fee_display,
        "grand_total": grand_total,
    }

    return render(request, "checkout/checkout.html", template_ctx)


def checkout_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    if not order.email_sent:
        subject = render_to_string(
            "checkout/confirmation_emails/confirmation_email_subject.txt",
            {"order": order}
        ).strip()

        body = render_to_string(
            "checkout/confirmation_emails/confirmation_email_body.txt",
            {
                "order": order,
                "contact_email": getattr(
                    settings,
                    "SUPPORT_EMAIL",
                    settings.DEFAULT_FROM_EMAIL
                ),
            }
        )

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [order.email],
            fail_silently=False,
        )

        order.email_sent = True
        order.save(update_fields=["email_sent"])

    messages.success(request, f"Order {order.order_number} placed successfully!")
    return render(request, "checkout/success.html", {"order": order})


@require_POST
def update_order_status(request, order_id):
    """
    Update the status of an order from the admin dashboard (synchronous, no live updates).
    """
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status')

    if new_status not in dict(Order.STATUS_CHOICES):
        messages.error(request, "Invalid status selected.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    order.status = new_status
    order.save()

    messages.success(request, f"Order {order.order_number} status updated to {new_status}.")
    return redirect(request.META.get('HTTP_REFERER', '/'))
