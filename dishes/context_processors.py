from django.core.cache import cache
from dishes.models import Category
from .models import Category


def menu_dishes(request):
    """Return all categories and dishes for menu dropdowns"""
    menu = {}
    for menu_type in ['Breakfast', 'Lunch', 'Grill', 'Drinks']:
        categories = Category.objects.filter(menu_type=menu_type)
        menu[menu_type] = {}
        for category in categories:
            menu[menu_type][category.name] = category.dishes.filter(available=True)
    return {'menu_dishes': menu}


def categories_nav(request):
    categories = cache.get('nav_categories')

    if categories is None:
        categories = list(Category.objects.only('name', 'slug'))
        cache.set('nav_categories', categories, 60 * 60)

    return {'categories': categories}
