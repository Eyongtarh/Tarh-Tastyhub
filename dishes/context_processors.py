from django.core.cache import cache
from dishes.models import Category


def menu_dishes(request):
    """
    Return all categories and their available dishes grouped by menu_type
    for menu dropdowns.
    """
    menu = cache.get('menu_dishes')

    if menu is None:
        menu = {}
        menu_types = ['Breakfast', 'Lunch', 'Grill', 'Drinks']
        for menu_type in menu_types:
            categories = Category.objects.filter(menu_type=menu_type).prefetch_related('dishes')
            menu[menu_type] = {
                category.name: category.dishes.filter(available=True)
                for category in categories
            }
        cache.set('menu_dishes', menu, 60 * 60)  # cache for 1 hour

    return {'menu_dishes': menu}


def categories_nav(request):
    """
    Return all categories for top navigation.
    """
    categories = cache.get('nav_categories')
    if categories is None:
        categories = list(Category.objects.only('name', 'slug'))
        cache.set('nav_categories', categories, 60 * 60)  # cache for 1 hour
    return {'categories': categories}
