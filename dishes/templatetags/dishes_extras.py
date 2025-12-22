from django import template
from dishes.models import Category

register = template.Library()


@register.filter
def get_category_dishes(categories, menu_type):
    """Return all dishes under a specific menu type."""
    dishes = []
    for category in categories.filter(menu_type=menu_type):
        dishes.extend(category.dishes.all())
    return dishes


@register.filter
def remove_keys(query_dict, keys):
    """
    Return a query string with the specified keys removed.
    Usage: {{ request.GET|remove_keys:"min_price,max_price" }}
    """
    if not query_dict:
        return ""
    qd = query_dict.copy()
    for key in keys.split(','):
        if key in qd:
            del qd[key]
    return qd.urlencode()
