from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.urls import reverse
from decimal import Decimal

from dishes.models import DishPortion
from bag.context_processors import MIN_FREE_DELIVERY, DEFAULT_DELIVERY


def _get_bag_totals(request):
    """
    Helper to compute subtotal, delivery fee, and grand total.
    Applies free delivery if subtotal >= MIN_FREE_DELIVERY.
    """
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
        "grand_total": grand_total
    }


def view_bag(request):
    """
    Render the bag page with all items and totals.
    """
    bag = request.session.get("bag", {})
    items = []

    for pid, qty in bag.items():
        portion = get_object_or_404(DishPortion.objects.select_related("dish"), pk=pid)
        line_total = portion.price * qty
        items.append({
            "portion": portion,
            "quantity": qty,
            "line_total": line_total
        })

    totals = _get_bag_totals(request)

    context = {
        "items": items,
        "bag_total": totals["subtotal"],
        "delivery_fee": totals["delivery_fee"],
        "delivery_fee_display": totals["delivery_fee_display"],
        "grand_total": totals["grand_total"]
    }
    return render(request, 'bag/card.html', context)


def add_to_bag(request, portion_id):
    """
    Adds a portion to the bag with the exact quantity from input.
    Overwrites previous quantity for this portion.
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid method")

    portion = get_object_or_404(DishPortion.objects.select_related("dish"), pk=portion_id)

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1
    if quantity < 1:
        quantity = 1

    bag = request.session.get("bag", {})
    bag[str(portion_id)] = quantity
    request.session["bag"] = bag
    request.session.modified = True

    message = f"Added {portion.dish.name} ({portion.size}) × {quantity} to your bag"

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        totals = _get_bag_totals(request)
        line_total = portion.price * quantity

        return JsonResponse({
            "success": True,
            "message": message,
            "bag_count": sum(bag.values()),
            "line_total": f"{line_total:.2f}",
            "subtotal": f"{totals['subtotal']:.2f}",
            "delivery_fee": f"{totals['delivery_fee']:.2f}",
            "delivery_fee_display": totals['delivery_fee_display'],
            "grand_total": f"{totals['grand_total']:.2f}",
        })

    messages.success(request, message)
    return redirect(request.POST.get("redirect_url", reverse("dish_list")))


def adjust_bag(request, portion_id):
    """
    Adjusts the quantity of a portion in the bag.
    Removes it if quantity is zero.
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid method")

    portion = get_object_or_404(DishPortion.objects.select_related("dish"), pk=portion_id)

    try:
        quantity = int(request.POST.get("quantity", 0))
    except (TypeError, ValueError):
        quantity = 0

    bag = request.session.get("bag", {})
    key = str(portion_id)

    if quantity > 0:
        bag[key] = quantity
    else:
        bag.pop(key, None)

    request.session["bag"] = bag
    request.session.modified = True

    totals = _get_bag_totals(request)
    line_total = portion.price * quantity if quantity > 0 else Decimal("0.00")

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "bag_count": sum(bag.values()),
            "line_total": f"{line_total:.2f}",
            "subtotal": f"{totals['subtotal']:.2f}",
            "delivery_fee": f"{totals['delivery_fee']:.2f}",
            "delivery_fee_display": totals['delivery_fee_display'],
            "grand_total": f"{totals['grand_total']:.2f}",
        })

    return redirect("bag")


def remove_from_bag(request, portion_id):
    """
    Removes a portion from the bag entirely.
    """
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
            "delivery_fee_display": totals['delivery_fee_display'],
            "grand_total": f"{totals['grand_total']:.2f}",
        })

    return redirect("bag")
