from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Order


@staff_member_required
def admin_dashboard(request):
    orders = Order.objects.all().prefetch_related('lineitems__portion__dish').order_by('-date')[:200]
    return render(request, 'checkout/admin_dashboard.html', {'orders': orders})


@staff_member_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            order.status = new_status
            order.save()
            messages.success(request, f"Order #{order.order_number} updated to {new_status}.")
    return redirect('admin_dashboard')
