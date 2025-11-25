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
