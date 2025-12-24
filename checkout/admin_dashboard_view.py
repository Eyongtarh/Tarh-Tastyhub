from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST

from .models import Order
from dishes.models import Dish, Category
from feedback.models import Feedback


STATUS_COLORS = {
    'Pending': 'warning',
    'Preparing': 'info',
    'Out for Delivery': 'orange',
    'Completed': 'success',
}


@staff_member_required
def admin_dashboard(request):
    """
    Staff-only dashboard view displaying:
    - Orders
    - All Dishes and Categories
    - Feedback messages
    """
    orders = (
        Order.objects
        .all()
        .prefetch_related('lineitems__portion__dish')
        .order_by('-date')[:200]
    )

    for order in orders:
        order.status_color = STATUS_COLORS.get(order.status, 'secondary')

    dishes = Dish.objects.all().select_related('category').order_by('name')
    categories = Category.objects.all().order_by('name')

    filter_status = request.GET.get("filter", "all")
    if filter_status == "unread":
        feedback_qs = Feedback.objects.filter(handled=False)
    elif filter_status == "handled":
        feedback_qs = Feedback.objects.filter(handled=True)
    else:
        feedback_qs = Feedback.objects.all()

    feedback_qs = feedback_qs.order_by('-created_at')
    paginator = Paginator(feedback_qs, 10)
    page_number = request.GET.get("page")
    feedback_list = paginator.get_page(page_number)

    context = {
        'orders': orders,
        'dishes': dishes,
        'categories': categories,
        'feedback_list': feedback_list,
        'filter_status': filter_status,
    }

    return render(
        request,
        'checkout/admin_dashboard.html',
        context
    )


@staff_member_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    if request.method != "POST":
        return redirect("admin_dashboard")

    new_status = request.POST.get("status")
    if not new_status:
        return redirect("admin_dashboard")

    old_status = order.status
    order.status = new_status
    order.save()

    messages.success(
        request,
        f"Order #{order.id} updated to '{new_status}'."
    )

    EMAIL_STATUSES = [
        "Preparing",
        "Out for Delivery",
        "Ready for Pickup",
        "Completed",
    ]

    if new_status not in EMAIL_STATUSES:
        return redirect("admin_dashboard")

    current_site = get_current_site(request)
    site_url = f"https://{current_site.domain}"

    subject = f"Your order #{order.order_number} is now {new_status}"

    address_lines = [order.street_address1]
    if order.street_address2:
        address_lines.append(order.street_address2)
    city_line = order.town_or_city
    if order.county:
        city_line += f", {order.county}"
    city_line += f", {order.local}"
    address_lines.append(city_line)
    delivery_address = "\n".join(address_lines)

    message = (
        f"Hi {order.full_name},\n\n"
        "Thanks for ordering from Tarh Tastyhub!\n\n"
        f"Your order #{order.order_number} status has been updated "
        f"to '{new_status}'.\n\n"
        f"Order Total: ₦{order.grand_total}\n"
        "Delivery Address:\n"
        f"{delivery_address}\n\n"
        f"If you have any questions, contact us at {site_url}/feedback/\n\n"
        "Bon appétit!\n"
        "The Tarh Tastyhub Team"
    )

    recipient_list = [order.email]

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )

    return redirect("admin_dashboard")


@staff_member_required
@require_POST
def mark_feedback_handled(request, feedback_id):
    """
    Mark a specific feedback entry as handled.
    """
    fb = get_object_or_404(Feedback, pk=feedback_id)
    fb.handled = True
    fb.save()
    return redirect('admin_dashboard')


@staff_member_required
@require_POST
def mark_feedback_unhandled(request, feedback_id):
    """
    Mark a specific feedback entry as unhandled.
    """
    fb = get_object_or_404(Feedback, pk=feedback_id)
    fb.handled = False
    fb.save()
    return redirect('admin_dashboard')


@staff_member_required
def cancel_order(request, order_id):
    """
    Cancel an order is only allowed if order is not already completed
    """
    order = get_object_or_404(Order, pk=order_id)

    if order.status == "Completed":
        messages.error(
            request,
            "Completed orders cannot be cancelled."
        )
        return redirect("admin_dashboard")

    if request.method == "POST":
        order.status = "Cancelled"
        order.save()
        messages.success(
            request,
            f"Order #{order.order_number} has been cancelled."
        )
        return redirect("admin_dashboard")

    context = {"order": order}
    return render(request, "checkout/cancel_order.html", context)
