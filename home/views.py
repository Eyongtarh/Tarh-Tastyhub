from django.shortcuts import render
from django.core.paginator import Paginator
from django.core.cache import cache

from dishes.models import Dish, Category


def index(request):
    """
    Homepage with:
    - Categories
    - Paginated Featured Dishes
    - Testimonials section (static on front-end)
    """
    categories = cache.get("home_categories")
    if categories is None:
        categories = list(
            Category.objects.filter(slug__isnull=False)
            .exclude(slug__exact="")
            .order_by("name")[:4]
        )
        cache.set("home_categories", categories, 3600)

    featured_qs = Dish.objects.available().order_by("-id")

    paginator = Paginator(featured_qs, 4)
    page_number = request.GET.get("page")
    featured_dishes = paginator.get_page(page_number)

    context = {
        "categories": categories,
        "featured_dishes": featured_dishes,
    }

    return render(request, "home/index.html", context)


def privacy_policy(request):
    """
    Privacy Policy page for Tarh Tastyhub.
    """
    return render(request, "privacy_policy.html")


def terms_and_conditions(request):
    """
    Terms & Conditions page for Tarh Tastyhub.
    """
    return render(request, "terms_and_conditions.html")
