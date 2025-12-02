from decimal import Decimal
from dishes.models import DishPortion
import logging

logger = logging.getLogger(__name__)

DEFAULT_DELIVERY = Decimal("4.00")
MIN_FREE_DELIVERY = Decimal("20.00")


def bag_contents(request):
    session_bag = request.session.get("bag", {})
    if not isinstance(session_bag, dict):
        session_bag = {}

    normalized = {}
    invalid_keys = []

    for raw_id, raw_qty in session_bag.items():
        try:
            portion_id = int(raw_id)
            qty = max(1, int(raw_qty))
        except Exception:
            invalid_keys.append(raw_id)
            continue
        normalized[str(portion_id)] = qty

    for key in invalid_keys:
        session_bag.pop(key, None)
    request.session["bag"] = session_bag
    request.session.modified = True

    portion_ids = [int(pid) for pid in normalized.keys()]
    portions = DishPortion.objects.select_related("dish").filter(id__in=portion_ids)
    portion_map = {p.id: p for p in portions}

    items = []
    total = Decimal("0.00")
    count = 0
    removed_missing_items = False

    for pid_str, qty in normalized.items():
        pid = int(pid_str)
        portion = portion_map.get(pid)
        if not portion:
            logger.warning(f"Bag contains missing DishPortion id={pid}; removing.")
            session_bag.pop(pid_str, None)
            removed_missing_items = True
            continue
        line_total = portion.price * qty
        total += line_total
        count += qty
        items.append({
            "portion_id": pid,
            "portion": portion,
            "dish": portion.dish,
            "quantity": qty,
            "price": portion.price,
            "line_total": line_total,
        })

    if removed_missing_items:
        request.session["bag"] = session_bag
        request.session.modified = True

    delivery_fee = Decimal("0.00") if total >= MIN_FREE_DELIVERY else DEFAULT_DELIVERY
    grand_total = total + delivery_fee

    return {
        "items": items,
        "bag_items": items,
        "bag_total": total,
        "delivery_fee": delivery_fee,
        "grand_total": grand_total,
        "bag_count": count,
    }
