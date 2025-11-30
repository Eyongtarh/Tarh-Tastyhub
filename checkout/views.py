from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import logging

from .forms import OrderForm
from .services import OrderService, OrderServiceError
from .models import Order  # make sure you have an Order model

logger = logging.getLogger(__name__)


def checkout(request):
    """
    View to handle checkout process
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
                order = OrderService.create_order_from_bag(
                    user=request.user if request.user.is_authenticated else None,
                    bag=bag,
                    form_data=form.cleaned_data
                )

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

    return render(request, 'checkout/checkout.html', {
        'form': form,
        **ctx
    })


def checkout_success(request, order_number):
    """
    View for the checkout success page.
    """
    order = get_object_or_404(Order, order_number=order_number)

    messages.success(request, f"Order {order.order_number} placed successfully!")
    return render(request, 'checkout/success.html', {'order': order})
