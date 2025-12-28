from decimal import Decimal, ROUND_HALF_UP
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.admin.views.decorators import staff_member_required

import stripe

from .forms import OrderForm
from .services import OrderService, OrderServiceError
from .models import Order

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
@require_POST
def cache_checkout_data(request):
    """
    Cache metadata in Stripe PaymentIntent if needed.
    """
    try:
        client_secret = request.POST.get("client_secret")
        if client_secret:
            pid = client_secret.split("_secret")[0]
            stripe.PaymentIntent.modify(
                pid,
                metadata={
                    "delivery_type": request.POST.get("delivery_type", ""),
                    "pickup_time": request.POST.get("pickup_time", ""),
                    "email": request.POST.get("email", ""),
                },
            )
        return JsonResponse({"status": "success"})
    except Exception as e:
        logger.exception("Failed to cache checkout data")
        return JsonResponse({"error": str(e)}, status=400)


def _to_decimal(value, fallback=Decimal("0.00")):
    try:
        return Decimal(str(value)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    except Exception:
        return fallback


# CHECKOUT VIEW
@require_http_methods(["GET", "POST"])
def checkout(request):
    from bag.context_processors import bag_contents

    ctx = bag_contents(request)
    bag = request.session.get("bag", {})

    if not bag:
        messages.error(request, "Your bag is empty.")
        return redirect("bag")

    subtotal = _to_decimal(ctx.get("bag_total", 0))
    MIN_FREE = _to_decimal(settings.FREE_DELIVERY_THRESHOLD)
    DEFAULT_DELIVERY = _to_decimal(settings.DEFAULT_DELIVERY_FEE)

    delivery_type = request.POST.get("delivery_type", "delivery")
    delivery_fee = (
        Decimal("0.00")
        if delivery_type == "pickup" or subtotal >= MIN_FREE
        else DEFAULT_DELIVERY
    )
    grand_total = (subtotal + delivery_fee).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    delivery_fee_display = "Free" if delivery_fee == 0 else f"${delivery_fee:.2f}"
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            try:
                stripe_pid = request.POST.get("stripe_pid")
                if stripe_pid and Order.objects.filter(stripe_pid=stripe_pid).exists():
                    existing = Order.objects.get(stripe_pid=stripe_pid)
                    return redirect(
                        "checkout_success",
                        order_number=existing.order_number,
                    )
                if stripe_pid:
                    intent = stripe.PaymentIntent.retrieve(stripe_pid)
                    if intent.status in ["requires_payment_method", "requires_confirmation"]:
                        stripe.PaymentIntent.confirm(stripe_pid)
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
                messages.success(request, "Order placed successfully!")
                return redirect(
                    "checkout_success",
                    order_number=order.order_number,
                )
            except OrderServiceError as e:
                messages.error(request, str(e))
            except Exception:
                logger.exception("Checkout error")
                messages.error(
                    request,
                    "Payment succeeded, but order creation failed.",
                )
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        # PREFILL FORM
        initial = {}
        if request.user.is_authenticated:
            profile = getattr(request.user, "userprofile", None)
            initial = {
                "full_name": request.user.get_full_name(),
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
    # STRIPE PAYMENT INTENT (GET)
    client_secret = None
    if request.method == "GET":
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(grand_total * 100),
                currency=settings.STRIPE_CURRENCY,
                automatic_payment_methods={"enabled": True},
                metadata={
                    "delivery_type": delivery_type,
                    "delivery_fee": str(delivery_fee),
                    "email": request.user.email if request.user.is_authenticated else "",
                    "username": request.user.username if request.user.is_authenticated else "AnonymousUser",
                },
            )
            client_secret = intent.client_secret
        except Exception:
            logger.exception("Stripe PaymentIntent creation failed")

    return render(
        request,
        "checkout/checkout.html",
        {
            "form": form,
            "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
            "client_secret": client_secret,
            "bag_items": ctx["bag_items"],
            "bag_total": subtotal,
            "delivery_fee": delivery_fee,
            "delivery_fee_display": delivery_fee_display,
            "grand_total": grand_total,
        },
    )
# CHECKOUT SUCCESS PAGE
def checkout_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    if not order.email_sent:
        subject = render_to_string(
            "checkout/confirmation_emails/confirmation_email_subject.txt",
            {"order": order},
        ).strip()

        body = render_to_string(
            "checkout/confirmation_emails/confirmation_email_body.txt",
            {"order": order, "current_site": request.get_host()},
        )
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [order.email],
        )
        order.email_sent = True
        order.save(update_fields=["email_sent"])

    return render(
        request,
        "checkout/success.html",
        {"order": order},
    )


# ADMIN UTILITIES
@require_POST
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get("status")

    if new_status not in dict(Order.STATUS_CHOICES):
        messages.error(request, "Invalid status.")
        return redirect(request.META.get("HTTP_REFERER", "/"))

    order.status = new_status
    order.save()

    messages.success(request, "Order status updated.")
    return redirect(request.META.get("HTTP_REFERER", "/"))


@staff_member_required
def print_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    html = render_to_string(
        "checkout/print_order.html",
        {"order": order},
    )
    return HttpResponse(html)
