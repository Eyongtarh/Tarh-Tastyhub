from django.shortcuts import render
from dishes.models import Dish, Category

def index(request):
    """
    Home page view for Tarh Tastyhub.
    """

    # Get 4 valid categories only (with slug)
    categories = Category.objects.filter(
        slug__isnull=False
    ).exclude(
        slug__exact=''
    ).order_by('name')[:4]

    # Featured dishes
    featured_dishes = Dish.objects.filter(
        available=True
    ).order_by('-id')[:8]

    context = {
        'categories': categories,
        'featured_dishes': featured_dishes,
    }

    return render(request, 'home/index.html', context)
