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
from .services import OrderService
from .models import Order

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


# CACHE CHECKOUT DATA
@csrf_exempt
@require_POST
def cache_checkout_data(request):
    """Store delivery choice in session AFTER user selection."""
    try:
        request.session["delivery_type"] = request.POST.get("delivery_type")
        request.session["pickup_time"] = request.POST.get("pickup_time")
        request.session["email"] = request.POST.get("email")
        return JsonResponse({"status": "ok"})
    except Exception as e:
        logger.exception("cache_checkout_data failed")
        return JsonResponse({"error": str(e)}, status=400)


# UTILS
def _to_decimal(value, fallback=Decimal("0.00")):
    try:
        return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except Exception:
        return fallback


# CHECKOUT
@require_http_methods(["GET", "POST"])
def checkout(request):
    from bag.context_processors import bag_contents
    ctx = bag_contents(request)
    bag = request.session.get("bag", {})

    if not bag:
        messages.error(request, "Your bag is empty.")
        return redirect("bag")

    subtotal = _to_decimal(ctx["bag_total"])
    delivery_fee = _to_decimal(ctx["delivery_fee"])
    grand_total = _to_decimal(ctx["grand_total"])
    delivery_fee_display = ctx["delivery_fee_display"]
    delivery_type = request.session.get("delivery_type")
    pickup_time = request.session.get("pickup_time")

    if delivery_type == "pickup":
        delivery_fee = Decimal("0.00")
        delivery_fee_display = "Free"
        grand_total = subtotal

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            # Add delivery info to form_data so OrderService gets it
            form.cleaned_data["delivery_fee"] = delivery_fee
            form.cleaned_data["delivery_type"] = delivery_type
            form.cleaned_data["pickup_time"] = pickup_time

            stripe_pid = request.POST.get("stripe_pid")
            if stripe_pid and Order.objects.filter(stripe_pid=stripe_pid).exists():
                order = Order.objects.get(stripe_pid=stripe_pid)
                return redirect("checkout_success", order_number=order.order_number)

            order = OrderService.create_order_from_bag(
                user=request.user if request.user.is_authenticated else None,
                bag=bag,
                form_data=form.cleaned_data,
                stripe_pid=stripe_pid,
            )

            # Clear session bag and delivery info
            request.session["bag"] = {}
            request.session.pop("delivery_type", None)
            request.session.pop("pickup_time", None)

            return redirect("checkout_success", order_number=order.order_number)
    else:
        form = OrderForm()
        intent = stripe.PaymentIntent.create(
            amount=int(grand_total * 100),
            currency=settings.STRIPE_CURRENCY,
            automatic_payment_methods={"enabled": True},
        )

    return render(
        request,
        "checkout/checkout.html",
        {
            "form": form,
            "client_secret": intent.client_secret,
            "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
            "bag_items": ctx["bag_items"],
            "bag_total": subtotal,
            "delivery_fee_display": delivery_fee_display,
            "grand_total": grand_total,
        },
    )


# CHECKOUT SUCCESS
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
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [order.email])
        order.email_sent = True
        order.save(update_fields=["email_sent"])

    # Prepare a display string for delivery fee
    if order.delivery_type == "pickup" or order.delivery_fee == 0:
        delivery_display = "Free"
    else:
        delivery_display = f"${order.delivery_fee:.2f}"

    return render(
        request,
        "checkout/success.html",
        {"order": order, "delivery_display": delivery_display},
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
    html = render_to_string("checkout/print_order.html", {"order": order})
    return HttpResponse(html)
