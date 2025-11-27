from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.urls import reverse
import logging

from .forms import OrderForm
from .services import OrderService, OrderServiceError

logger = logging.getLogger(__name__)


def checkout(request):
    from bag.context_processors import bag_contents
    ctx = bag_contents(request)
    bag = request.session.get('bag', {})

    if not bag:
        messages.error(request, "Your bag is empty. Add items before checkout.")
        return redirect('view_bag')

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

                messages.success(request, '<span class="fa-icon"><i class="fa-solid fa-check"></i></span> Order placed successfully!')
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
                    'phone_number': profile.default_phone_number,
                    'street_address1': profile.default_street_address1,
                    'street_address2': profile.default_street_address2,
                    'town_or_city': profile.default_town_or_city,
                    'county': profile.default_county,
                    'postcode': profile.default_postcode,
                    'local': profile.default_local,
                }
        form = OrderForm(initial=initial)

    return render(request, 'checkout/checkout.html', {
        'form': form,
        **ctx
    })
