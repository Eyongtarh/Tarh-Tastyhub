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


@csrf_exempt
@require_POST
def cache_checkout_data(request):
    try:
        stripe_pid = request.POST.get("stripe_pid")

        if stripe_pid:
            stripe.PaymentIntent.modify(
                stripe_pid,
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
    delivery_fee = Decimal("0.00")
    grand_total = subtotal + delivery_fee

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
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

            request.session["bag"] = {}
            return redirect("checkout_success", order_number=order.order_number)
    else:
        form = OrderForm()

        intent = stripe.PaymentIntent.create(
            amount=int(grand_total * 100),
            currency=settings.STRIPE_CURRENCY,
            automatic_payment_methods={"enabled": True},
        )

    return render(request, "checkout/checkout.html", {
        "form": form,
        "client_secret": intent.client_secret,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
        "bag_items": ctx["bag_items"],
        "bag_total": subtotal,
        "delivery_fee_display": "Free",
        "grand_total": grand_total,
    })


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
