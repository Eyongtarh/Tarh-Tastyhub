# bag/views.py
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.urls import reverse
from dishes.models import DishPortion
from bag.context_processors import MIN_FREE_DELIVERY, DEFAULT_DELIVERY

MAX_PER_DISH_PER_DAY = 20


def _auth_required_response(request):
    """
    Returns proper response when user is not authenticated.
    Works for both AJAX and normal requests.
    """
    message = "Please log in or sign up to add items to your bag."
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "success": False,
            "error": "AUTH_REQUIRED",
            "message": message,
        }, status=401)
    messages.error(request, message)
    return redirect(reverse("account_login"))


def _get_bag_totals(request):
    bag = request.session.get("bag", {})
    subtotal = Decimal("0.00")
    for pid, qty in bag.items():
        portion = DishPortion.objects.get(pk=pid)
        subtotal += portion.price * qty
    if subtotal >= MIN_FREE_DELIVERY:
        delivery_fee = Decimal("0.00")
        delivery_fee_display = "Free"
    else:
        delivery_fee = DEFAULT_DELIVERY
        delivery_fee_display = f"${DEFAULT_DELIVERY:.2f}"
    grand_total = subtotal + delivery_fee
    return {
        "subtotal": subtotal,
        "delivery_fee": delivery_fee,
        "delivery_fee_display": delivery_fee_display,
        "grand_total": grand_total,
    }


def view_bag(request):
    if not request.user.is_authenticated:
        return _auth_required_response(request)
    bag = request.session.get("bag", {})
    items = []
    for pid, qty in bag.items():
        portion = get_object_or_404(
            DishPortion.objects.select_related("dish"),
            pk=pid
        )
        line_total = portion.price * qty
        items.append({
            "portion": portion,
            "quantity": qty,
            "line_total": line_total,
        })
    totals = _get_bag_totals(request)
    context = {
        "items": items,
        "bag_total": totals["subtotal"],
        "delivery_fee": totals["delivery_fee"],
        "delivery_fee_display": totals["delivery_fee_display"],
        "grand_total": totals["grand_total"],
    }
    return render(request, "bag/card.html", context)


def add_to_bag(request, portion_id):
    if not request.user.is_authenticated:
        return _auth_required_response(request)
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid method")
    portion = get_object_or_404(
        DishPortion.objects.select_related("dish"),
        pk=portion_id
    )
    try:
        requested_quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        requested_quantity = 1
    requested_quantity = max(1, requested_quantity)
    bag = request.session.get("bag", {})
    existing_quantity = bag.get(str(portion_id), 0)
    if existing_quantity + requested_quantity > MAX_PER_DISH_PER_DAY:
        message = (
            f"You can only order up to {MAX_PER_DISH_PER_DAY} "
            "of this dish per day."
        )
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "success": False,
                "error": "DAILY_LIMIT_REACHED",
                "message": message,
            })
        messages.error(request, message)
        return redirect(reverse("dish_list"))
    bag[str(portion_id)] = existing_quantity + requested_quantity
    request.session["bag"] = bag
    request.session.modified = True
    message = (
        f"Added {portion.dish.name} ({portion.size}) × {requested_quantity} "
        "to your bag"
    )
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        totals = _get_bag_totals(request)
        line_total = portion.price * bag[str(portion_id)]
        return JsonResponse({
            "success": True,
            "message": message,
            "bag_count": sum(bag.values()),
            "line_total": f"{line_total:.2f}",
            "subtotal": f"{totals['subtotal']:.2f}",
            "delivery_fee": f"{totals['delivery_fee']:.2f}",
            "delivery_fee_display": totals["delivery_fee_display"],
            "grand_total": f"{totals['grand_total']:.2f}",
        })
    messages.success(request, message)
    return redirect(reverse("dish_list"))


def adjust_bag(request, portion_id):
    if not request.user.is_authenticated:
        return _auth_required_response(request)
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid method")
    portion = get_object_or_404(
        DishPortion.objects.select_related("dish"),
        pk=portion_id
    )
    try:
        requested_quantity = int(request.POST.get("quantity", 0))
    except (TypeError, ValueError):
        requested_quantity = 0
    requested_quantity = max(0, requested_quantity)
    if requested_quantity > MAX_PER_DISH_PER_DAY:
        message = (
            f"You can only order up to {MAX_PER_DISH_PER_DAY} "
            "of this dish per day."
        )
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "success": False,
                "error": "DAILY_LIMIT_REACHED",
                "message": message,
            })
        messages.error(request, message)
        requested_quantity = MAX_PER_DISH_PER_DAY
    bag = request.session.get("bag", {})
    key = str(portion_id)
    if requested_quantity > 0:
        bag[key] = requested_quantity
    else:
        bag.pop(key, None)
    request.session["bag"] = bag
    request.session.modified = True
    totals = _get_bag_totals(request)
    line_total = (
        portion.price * requested_quantity
        if requested_quantity
        else Decimal("0.00")
    )
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "bag_count": sum(bag.values()),
            "line_total": f"{line_total:.2f}",
            "subtotal": f"{totals['subtotal']:.2f}",
            "delivery_fee": f"{totals['delivery_fee']:.2f}",
            "delivery_fee_display": totals["delivery_fee_display"],
            "grand_total": f"{totals['grand_total']:.2f}",
        })
    return redirect("bag")


def remove_from_bag(request, portion_id):
    if not request.user.is_authenticated:
        return _auth_required_response(request)
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid method")
    bag = request.session.get("bag", {})
    bag.pop(str(portion_id), None)
    request.session["bag"] = bag
    request.session.modified = True
    totals = _get_bag_totals(request)
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "bag_count": sum(bag.values()),
            "line_total": "0.00",
            "subtotal": f"{totals['subtotal']:.2f}",
            "delivery_fee": f"{totals['delivery_fee']:.2f}",
            "delivery_fee_display": totals["delivery_fee_display"],
            "grand_total": f"{totals['grand_total']:.2f}",
        })

    return redirect("bag")
