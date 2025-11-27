from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.urls import reverse
from decimal import Decimal

from dishes.models import DishPortion


def view_bag(request):
    """
    Renders the bag view. All bag totals are calculated server-side
    in the bag_contents context processor.
    """
    return render(request, 'bag/card.html')


def add_to_bag(request, portion_id):
    """
    Secure add-to-bag:
    - Validates portion exists
    - Never trusts price from client
    - Enforces minimum quantity = 1
    - Works with AJAX or normal form POST
    """
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid method")

    portion = get_object_or_404(
        DishPortion.objects.select_related("dish"),
        pk=portion_id
    )

    # Validate quantity
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    bag = request.session.get("bag", {})
    key = str(portion_id)

    # Add or increase quantity
    bag[key] = bag.get(key, 0) + quantity

    request.session["bag"] = bag
    request.session.modified = True

    message = f"Added {portion.dish.name} ({portion.size}) × {quantity} to your bag"

    # AJAX Response
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        from bag.context_processors import bag_contents
        ctx = bag_contents(request)

        # Compute accurate server-side line total
        line_total = portion.price * bag[key]

        return JsonResponse({
            "success": True,
            "message": message,
            "bag_count": ctx["bag_count"],
            "line_total": f"{line_total:.2f}",
            "grand_total": f"{ctx['grand_total']:.2f}",
        })

    messages.success(request, message)
    return redirect(request.POST.get("redirect_url", reverse("dish_list")))


def adjust_bag(request, portion_id):
    """
    Adjusts quantity or removes an item.
    POST expects:
        quantity > 0 — update
        quantity = 0 — remove
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid method")

    portion = get_object_or_404(
        DishPortion.objects.select_related("dish"),
        pk=portion_id
    )

    try:
        quantity = int(request.POST.get("quantity", 0))
    except (TypeError, ValueError):
        quantity = 0

    bag = request.session.get("bag", {})
    key = str(portion_id)

    if quantity > 0:
        bag[key] = quantity
        message = f"Updated {portion.dish.name} ({portion.size}) to {quantity}"
    else:
        bag.pop(key, None)
        message = f"Removed {portion.dish.name} ({portion.size})"

    request.session["bag"] = bag
    request.session.modified = True

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        from bag.context_processors import bag_contents
        ctx = bag_contents(request)

        line_total = portion.price * quantity if quantity > 0 else Decimal("0.00")

        return JsonResponse({
            "success": True,
            "message": message,
            "bag_count": ctx["bag_count"],
            "line_total": f"{line_total:.2f}",
            "grand_total": f"{ctx['grand_total']:.2f}",
        })

    messages.success(request, message)
    return redirect("bag")


def remove_from_bag(request, portion_id):
    """
    Remove a portion completely from the bag.
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid method")

    portion = get_object_or_404(
        DishPortion.objects.select_related("dish"),
        pk=portion_id
    )

    bag = request.session.get("bag", {})
    bag.pop(str(portion_id), None)

    request.session["bag"] = bag
    request.session.modified = True

    message = f"Removed {portion.dish.name} ({portion.size})"

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        from bag.context_processors import bag_contents
        ctx = bag_contents(request)

        return JsonResponse({
            "success": True,
            "message": message,
            "bag_count": ctx["bag_count"],
            "grand_total": f"{ctx['grand_total']:.2f}",
        })

    messages.success(request, message)
    return redirect("bag")
