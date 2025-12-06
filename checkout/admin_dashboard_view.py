from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Order
from dishes.models import Dish, Category


STATUS_COLORS = {
    'Pending': 'warning',
    'Preparing': 'info',
    'Out for Delivery': 'orange',
    'Completed': 'success',
}


@staff_member_required
def admin_dashboard(request):
    """
    Staff-only dashboard that displays:
    - Recent orders
    - All dishes
    - All categories
    """
    orders = (
        Order.objects
        .all()
        .prefetch_related('lineitems__portion__dish')
        .order_by('-date')[:200]
    )

    dishes = Dish.objects.all().select_related('category').order_by('name')
    categories = Category.objects.all().order_by('name')

    for order in orders:
        order.status_color = STATUS_COLORS.get(order.status, 'secondary')

    context = {
        'orders': orders,
        'dishes': dishes,
        'categories': categories,
    }
    return render(request, 'checkout/admin_dashboard.html', context)


@staff_member_required
def update_order_status(request, order_id):
    """
    Update the status of an order from the admin dashboard dropdown.
    """
    order = get_object_or_404(Order, pk=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')

        if new_status:
            order.status = new_status
            order.save()

            messages.success(
                request,
                f"Order #{order.id} status updated to '{new_status}'."
            )

    return redirect('admin_dashboard')
