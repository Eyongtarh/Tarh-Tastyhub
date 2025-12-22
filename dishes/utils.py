from django.core.cache import cache
from .models import Category


def get_cached_categories():
    """Return all categories cached for 1 hour."""
    key = "cached_category_menu"
    categories = cache.get(key)
    if not categories:
        categories = Category.objects.all().order_by("name")
        cache.set(key, categories, 3600)  # cache for 1 hour
    return categories
