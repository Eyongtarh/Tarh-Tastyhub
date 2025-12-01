from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
import logging

from .forms import OrderForm
from .services import OrderService, OrderServiceError
from .models import Order

logger = logging.getLogger(__name__)


def checkout(request):
    """
    Handle checkout process safely to prevent duplicate orders.
    """
    from bag.context_processors import bag_contents
    ctx = bag_contents(request)
    bag = request.session.get('bag', {})

    if not bag:
        messages.error(request, "Your bag is empty. Add items before checkout.")
        return redirect('bag')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            try:
                # Optional: Stripe PID from frontend for webhook consistency
                stripe_pid = request.POST.get('stripe_pid', None)

                # Check if order already exists with this stripe_pid
                if stripe_pid and Order.objects.filter(stripe_pid=stripe_pid).exists():
                    order = Order.objects.get(stripe_pid=stripe_pid)
                    messages.info(request, "Order already processed.")
                    return redirect('checkout_success', order_number=order.order_number)

                # Create order atomically
                order, _ = OrderService.create_order_from_bag(
                    user=request.user if request.user.is_authenticated else None,
                    bag=bag,
                    form_data=form.cleaned_data,
                    stripe_pid=stripe_pid
                )

                # Clear bag after success
                request.session['bag'] = {}
                request.session.modified = True

                messages.success(
                    request,
                    '<span class="fa-icon"><i class="fa-solid fa-check"></i></span> Order placed successfully!'
                )
                return redirect('checkout_success', order_number=order.order_number)

            except OrderServiceError as e:
                logger.exception(f"OrderServiceError during checkout: {e}")
                messages.error(request, str(e))
            except Exception as e:
                logger.exception(f"Unexpected error during checkout: {e}")
                messages.error(request, "Error processing your order. Please try again.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # Pre-fill form if user is authenticated
        initial = {}
        if request.user.is_authenticated:
            profile = getattr(request.user, 'userprofile', None)
            if profile:
                initial = {
                    'full_name': request.user.get_full_name() or request.user.username,
                    'email': request.user.email,
                    'phone_number': getattr(profile, 'default_phone_number', ''),
                    'street_address1': getattr(profile, 'default_street_address1', ''),
                    'street_address2': getattr(profile, 'default_street_address2', ''),
                    'town_or_city': getattr(profile, 'default_town_or_city', ''),
                    'county': getattr(profile, 'default_county', ''),
                    'postcode': getattr(profile, 'default_postcode', ''),
                    'local': getattr(profile, 'default_local', ''),
                }
        form = OrderForm(initial=initial)

    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    client_secret = settings.STRIPE_SECRET_KEY

    return render(request, 'checkout/checkout.html', {
        'form': form,
        'stripe_public_key': stripe_public_key,
        'client_secret': client_secret,
        **ctx
    })


def checkout_success(request, order_number):
    """
    View for the checkout success page.
    """
    order = get_object_or_404(Order, order_number=order_number)

    messages.success(request, f"Order {order.order_number} placed successfully!")
    return render(request, 'checkout/success.html', {'order': order})
