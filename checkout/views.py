"""
Checkout and order processing views.
Takes care of Stripe checkout data caching, order creation
from the shopping bag, payment intent creation, checkout success
flow, order status updates, and staff utilities such as printing orders.
"""
from decimal import Decimal, ROUND_HALF_UP
import logging
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.admin.views.decorators import staff_member_required
import stripe
from .forms import OrderForm
from .services import OrderService
from .models import Order

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
@require_POST
def cache_checkout_data(request):
    try:
        pid = request.POST.get("stripe_pid")
        if not pid or pid != request.session.get("stripe_pid"):
            return JsonResponse(
                {"error": "Payment intent does not match this session."},
                status=403,
            )
        delivery_type = request.POST.get("delivery_type", "delivery")
        pickup_time = request.POST.get("pickup_time", "")
        stripe.PaymentIntent.modify(
            pid,
            metadata={
                "bag": json.dumps(request.session.get("bag", {})),
                "delivery_type": delivery_type,
                "pickup_time": pickup_time,
                "email": request.POST.get("email", ""),
                "username": (
                    request.user.username
                    if request.user.is_authenticated
                    else "AnonymousUser"
                ),
            },
        )
        return JsonResponse({"status": "ok"})
    except Exception as e:
        logger.exception("cache_checkout_data failed")
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@require_POST
def create_payment_intent(request):
    """
    Creates the Stripe PaymentIntent the checkout page needs, out of
    band from rendering that page. Creating it inline in checkout()
    meant every GET /checkout/ blocked on a live network round trip to
    Stripe before Django could respond at all - moving it here lets
    the page render immediately and fetch this once loaded instead.
    """
    from bag.context_processors import bag_contents

    bag = request.session.get("bag", {})
    if not bag:
        return JsonResponse({"error": "Your bag is empty."}, status=400)
    ctx = bag_contents(request)
    delivery_type = request.session.get("delivery_type", "delivery")
    if delivery_type == "pickup":
        grand_total = Decimal(str(ctx["bag_total"]))
    else:
        grand_total = Decimal(str(ctx["grand_total"]))
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(grand_total * 100),
            currency=settings.STRIPE_CURRENCY,
            automatic_payment_methods={"enabled": True},
        )
    except Exception as e:
        logger.exception("create_payment_intent failed")
        return JsonResponse({"error": str(e)}, status=400)
    request.session["stripe_pid"] = intent.id
    return JsonResponse({"client_secret": intent.client_secret})


def _to_decimal(value, fallback=Decimal("0.00")):
    try:
        return Decimal(str(value)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )
    except Exception:
        return fallback


@require_http_methods(["GET", "POST"])
def checkout(request):
    from bag.context_processors import bag_contents
    ctx = bag_contents(request)
    bag = request.session.get("bag", {})
    if not bag:
        messages.error(request, "Your bag is empty.")
        return redirect("bag")
    subtotal = Decimal(str(ctx["bag_total"]))
    delivery_fee = Decimal(str(ctx["delivery_fee"]))
    grand_total = Decimal(str(ctx["grand_total"]))
    delivery_fee_display = ctx["delivery_fee_display"]
    delivery_type = request.session.get("delivery_type", "delivery")
    pickup_time = request.session.get("pickup_time")
    if delivery_type == "pickup":
        delivery_fee = Decimal("0.00")
        delivery_fee_display = "Free"
        grand_total = subtotal
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            delivery_type = (
                form.cleaned_data.get("delivery_type") or "delivery"
            )
            pickup_time = form.cleaned_data.get("pickup_time")
            form.cleaned_data["delivery_fee"] = delivery_fee
            form.cleaned_data["delivery_type"] = delivery_type
            form.cleaned_data["pickup_time"] = pickup_time
            stripe_pid = request.POST.get("stripe_pid")
            if (
                stripe_pid
                and Order.objects.filter(stripe_pid=stripe_pid).exists()
            ):
                order = Order.objects.get(stripe_pid=stripe_pid)
                return redirect(
                    "checkout_success",
                    order_number=order.order_number
                )
            order = OrderService.create_order_from_bag(
                user=request.user if request.user.is_authenticated else None,
                bag=bag,
                form_data=form.cleaned_data,
                stripe_pid=stripe_pid,
            )
            request.session["bag"] = {}
            request.session.pop("delivery_type", None)
            request.session.pop("pickup_time", None)
            return redirect(
                "checkout_success",
                order_number=order.order_number
            )
    else:
        form = OrderForm()
    return render(
        request,
        "checkout/checkout.html",
        {
            "form": form,
            "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
            "bag_items": ctx["bag_items"],
            "bag_total": subtotal,
            "delivery_fee_display": delivery_fee_display,
            "grand_total": grand_total,
        },
    )


def checkout_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    if not order.email_sent:
        current_site = get_current_site(request)
        subject = render_to_string(
            "checkout/confirmation_emails/confirmation_email_subject.txt",
            {"order": order},
        ).strip()
        body = render_to_string(
            "checkout/confirmation_emails/confirmation_email_body.txt",
            {"order": order, "current_site": current_site},
        )
        try:
            send_mail(
                subject, body, settings.DEFAULT_FROM_EMAIL, [order.email]
            )
            order.email_sent = True
            order.save(update_fields=["email_sent"])
        except Exception:
            # The order is already paid for and created at this point -
            # a broken SMTP config shouldn't turn a successful purchase
            # into a 500 error page for the customer.
            logger.exception(
                "Confirmation email failed for order %s", order.order_number
            )
    if order.delivery_type == "pickup" or order.delivery_fee == 0:
        delivery_display = "Free"
    else:
        delivery_display = f"${order.delivery_fee:.2f}"
    return render(
        request,
        "checkout/success.html",
        {"order": order, "delivery_display": delivery_display},
    )


@staff_member_required
def print_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    html = render_to_string("checkout/print_order.html", {"order": order})
    return HttpResponse(html)
