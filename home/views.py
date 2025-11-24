from django.shortcuts import render
from dishes.models import Dish


def index(request):
    """
    Home page view for Tarh Tastyhub.

    Shows:
    - Up to 4 unique dish categories (string values from Dish.category choices)
    - Up to 8 latest available dishes
    """

    # Extract 4 unique category names
    categories = Dish.objects.values_list('category', flat=True).distinct()[:4]

    # Featured dishes
    featured_dishes = Dish.objects.filter(available=True).order_by('-id')[:8]

    context = {
        'categories': categories,
        'featured_dishes': featured_dishes,
    }

    return render(request, 'home/index.html', context)
