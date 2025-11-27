from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .models import Order
from django.contrib import messages
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import re


def _safe_group_name(order_number):
    return re.sub(r'[^A-Za-z0-9_\-]', '_', f'order_{order_number}')


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

            progress = order.progress_percent

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                _safe_group_name(order.order_number),
                {
                    'type': 'order_update',
                    'status': order.status,
                    'progress': progress,
                }
            )

            async_to_sync(channel_layer.group_send)(
                'admin_orders',
                {
                    'type': 'order_update',
                    'id': order.id,
                    'status': order.status,
                }
            )
    return redirect('admin_dashboard')
