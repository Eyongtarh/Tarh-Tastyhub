from django.shortcuts import render, get_object_or_404
from .models import Order


def order_tracking(request, order_number):
    """
    Display the order tracking page showing the current order status
    and progress percentage for a specific order.
    """
    order = get_object_or_404(Order, order_number=order_number)
    return render(
        request,
        'checkout/order_tracking.html',
        {
            'order': order,
            'progress_percent': order.progress_percent,
        },
    )
