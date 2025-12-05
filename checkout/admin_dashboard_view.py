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
    orders = Order.objects.all().prefetch_related('lineitems__portion__dish').order_by('-date')[:200]
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
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            order.status = new_status
            order.save()
            messages.success(request, f"Order #{order.id} updated to {new_status}.")
    return redirect('admin_dashboard')


@staff_member_required
def delete_dish(request, slug):
    dish = get_object_or_404(Dish, slug=slug)
    if request.method == 'POST':
        dish.delete()
        messages.success(request, f"Dish '{dish.name}' deleted successfully.")
        return redirect('admin_dashboard')
    return render(request, 'dishes/delete_dish.html', {'dish': dish})


@staff_member_required
def delete_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    if request.method == 'POST':
        category.delete()
        messages.success(request, f"Category '{category.name}' deleted successfully.")
        return redirect('admin_dashboard')
    return render(request, 'dishes/delete_category.html', {'category': category})
